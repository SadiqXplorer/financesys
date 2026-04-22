const state = {
    accounts: [],
    categories: [],
};

const currency = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 2,
});

const API_BASE =
    window.location.port === "8000"
        ? ""
        : `${window.location.protocol}//${window.location.hostname || "127.0.0.1"}:8000`;

const STORAGE_KEY = "finance_system_local_data_v1";
let useLocalMode = false;

const defaultLocalData = {
    nextAccountId: 3,
    nextCategoryId: 10,
    nextTransactionId: 1,
    nextBudgetId: 1,
    accounts: [
        { id: 1, name: "Primary Bank", type: "Bank", balance: 0, created_at: new Date().toISOString() },
        { id: 2, name: "Cash Wallet", type: "Cash", balance: 0, created_at: new Date().toISOString() },
    ],
    categories: [
        { id: 1, name: "Salary", type: "income" },
        { id: 2, name: "Freelance", type: "income" },
        { id: 3, name: "Food", type: "expense" },
        { id: 4, name: "Transport", type: "expense" },
        { id: 5, name: "Bills", type: "expense" },
        { id: 6, name: "Entertainment", type: "expense" },
        { id: 7, name: "Mutual Fund", type: "investment" },
        { id: 8, name: "Stocks", type: "investment" },
        { id: 9, name: "Savings Deposit", type: "investment" },
    ],
    transactions: [],
    budgets: [],
};

function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    if (!toast) {
        return;
    }
    toast.textContent = message;
    toast.classList.remove("hidden");
    toast.style.background = isError ? "#8f2d2d" : "#1c1917";
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 2800);
}

function loadLocalData() {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultLocalData));
        return structuredClone(defaultLocalData);
    }
    try {
        return { ...structuredClone(defaultLocalData), ...JSON.parse(raw) };
    } catch {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultLocalData));
        return structuredClone(defaultLocalData);
    }
}

function saveLocalData(data) {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function getMonthKey(dateString) {
    return String(dateString).slice(0, 7);
}

function localDashboard(data) {
    const month = new Date().toISOString().slice(0, 7);
    const monthlyIncome = data.transactions
        .filter((t) => t.type === "income" && getMonthKey(t.transaction_date) === month)
        .reduce((sum, t) => sum + Number(t.amount), 0);
    const monthlyExpense = data.transactions
        .filter((t) => t.type === "expense" && getMonthKey(t.transaction_date) === month)
        .reduce((sum, t) => sum + Number(t.amount), 0);
    const monthlyInvestment = data.transactions
        .filter((t) => t.type === "investment" && getMonthKey(t.transaction_date) === month)
        .reduce((sum, t) => sum + Number(t.amount), 0);

    const recentTransactions = [...data.transactions]
        .sort((a, b) => `${b.transaction_date}-${b.id}`.localeCompare(`${a.transaction_date}-${a.id}`))
        .slice(0, 6)
        .map((transaction) => {
            const account = data.accounts.find((item) => item.id === Number(transaction.account_id));
            const category = data.categories.find((item) => item.id === Number(transaction.category_id));
            return {
                ...transaction,
                account_name: account ? account.name : "-",
                category_name: category ? category.name : "-",
            };
        });

    const budgetProgress = data.budgets.map((budget) => {
        const category = data.categories.find((item) => item.id === Number(budget.category_id));
        const spentAmount = data.transactions
            .filter(
                (transaction) =>
                    transaction.type === "expense" &&
                    Number(transaction.category_id) === Number(budget.category_id) &&
                    getMonthKey(transaction.transaction_date) === budget.month
            )
            .reduce((sum, transaction) => sum + Number(transaction.amount), 0);
        return {
            ...budget,
            category_name: category ? category.name : "-",
            spent_amount: spentAmount,
        };
    });

    const expenseByCategory = data.categories
        .filter((category) => category.type === "expense")
        .map((category) => {
            const total = data.transactions
                .filter(
                    (transaction) =>
                        transaction.type === "expense" &&
                        Number(transaction.category_id) === Number(category.id) &&
                        getMonthKey(transaction.transaction_date) === month
                )
                .reduce((sum, transaction) => sum + Number(transaction.amount), 0);
            return {
                category_name: category.name,
                total,
            };
        })
        .filter((item) => item.total > 0)
        .sort((a, b) => b.total - a.total);

    return {
        summary: {
            total_balance: data.accounts.reduce((sum, account) => sum + Number(account.balance), 0),
            monthly_income: monthlyIncome,
            monthly_expense: monthlyExpense,
            monthly_investment: monthlyInvestment,
            net_savings: monthlyIncome - monthlyExpense - monthlyInvestment,
        },
        recent_transactions: recentTransactions,
        budget_progress: budgetProgress,
        expense_by_category: expenseByCategory,
        active_month: month,
    };
}

function localApi(path, options = {}) {
    const method = (options.method || "GET").toUpperCase();
    const data = loadLocalData();
    const payload = options.body ? JSON.parse(options.body) : {};

    if (path === "/api/accounts" && method === "GET") {
        return { accounts: [...data.accounts].sort((a, b) => b.id - a.id) };
    }

    if (path === "/api/categories" && method === "GET") {
        return {
            categories: [...data.categories].sort((a, b) => a.type.localeCompare(b.type) || a.name.localeCompare(b.name)),
        };
    }

    if (path === "/api/dashboard" && method === "GET") {
        return localDashboard(data);
    }

    if (path === "/api/accounts" && method === "POST") {
        const account = {
            id: data.nextAccountId++,
            name: String(payload.name || "").trim(),
            type: String(payload.type || "").trim(),
            balance: Number(payload.balance || 0),
            created_at: new Date().toISOString(),
        };
        data.accounts.push(account);
        saveLocalData(data);
        return { account };
    }

    if (path === "/api/categories" && method === "POST") {
        const category = {
            id: data.nextCategoryId++,
            name: String(payload.name || "").trim(),
            type: String(payload.type || "").trim().toLowerCase(),
        };
        data.categories.push(category);
        saveLocalData(data);
        return { category };
    }

    if (path === "/api/budgets" && method === "POST") {
        const existing = data.budgets.find(
            (budget) =>
                Number(budget.category_id) === Number(payload.category_id) &&
                String(budget.month) === String(payload.month)
        );
        if (existing) {
            existing.amount_limit = Number(payload.amount_limit || 0);
            saveLocalData(data);
            return { budget: existing };
        }
        const budget = {
            id: data.nextBudgetId++,
            category_id: Number(payload.category_id),
            month: String(payload.month),
            amount_limit: Number(payload.amount_limit || 0),
        };
        data.budgets.push(budget);
        saveLocalData(data);
        return { budget };
    }

    if (path === "/api/transactions" && method === "POST") {
        const transaction = {
            id: data.nextTransactionId++,
            account_id: Number(payload.account_id),
            category_id: Number(payload.category_id),
            type: String(payload.type || "").trim().toLowerCase(),
            amount: Number(payload.amount || 0),
            note: String(payload.note || "").trim(),
            transaction_date: String(payload.transaction_date || "").trim(),
        };
        data.transactions.push(transaction);
        const account = data.accounts.find((item) => item.id === transaction.account_id);
        if (account) {
            account.balance += transaction.type === "income" ? transaction.amount : -transaction.amount;
        }
        saveLocalData(data);
        return { transaction };
    }

    if (path === "/api/reset" && method === "POST") {
        saveLocalData(structuredClone(defaultLocalData));
        return { message: "Clean default data restored" };
    }

    throw new Error("Unsupported offline action");
}

async function api(path, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${path}`, {
            headers: { "Content-Type": "application/json" },
            ...options,
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "Request failed");
        }
        return data;
    } catch (error) {
        useLocalMode = true;
        return localApi(path, options);
    }
}

function populateAccountOptions() {
    const select = document.getElementById("transaction-account");
    const accountsList = document.getElementById("accounts-list");
    if (select) {
        select.innerHTML = state.accounts
            .map((account) => `<option value="${account.id}">${account.name} (${account.type})</option>`)
            .join("");
    }

    if (accountsList) {
        accountsList.innerHTML = state.accounts
            .map(
                (account) => `
            <div class="stack-item">
                <div class="stack-item-head">
                    <strong>${account.name}</strong>
                    <span>${currency.format(account.balance)}</span>
                </div>
                <p>${account.type}</p>
            </div>
        `
            )
            .join("");
    }
}

function populateCategoryOptions() {
    const transactionTypeNode = document.getElementById("transaction-type");
    const transactionSelect = document.getElementById("transaction-category");
    const budgetSelect = document.getElementById("budget-category");
    const transactionType = transactionTypeNode ? transactionTypeNode.value : "expense";
    const filtered = state.categories.filter((category) => category.type === transactionType);
    const expenseCategories = state.categories.filter((category) => category.type === "expense");

    if (transactionSelect) {
        transactionSelect.innerHTML = filtered
            .map((category) => `<option value="${category.id}">${category.name}</option>`)
            .join("");
    }

    if (budgetSelect) {
        budgetSelect.innerHTML = expenseCategories
            .map((category) => `<option value="${category.id}">${category.name}</option>`)
            .join("");
    }
}

function renderTransactions(transactions) {
    const body = document.getElementById("transaction-table-body");
    if (!body) {
        return;
    }
    body.innerHTML = transactions
        .map(
            (transaction) => `
            <tr>
                <td>${transaction.transaction_date}</td>
                <td><span class="chip ${transaction.type}">${transaction.type}</span></td>
                <td>${transaction.category_name}</td>
                <td>${transaction.account_name}</td>
                <td>${currency.format(transaction.amount)}</td>
                <td>${transaction.note || "-"}</td>
            </tr>
        `
        )
        .join("");
}

function renderBudgetProgress(items) {
    const container = document.getElementById("budget-progress-list");
    if (!container) {
        return;
    }
    container.innerHTML = items.length
        ? items
              .map((item) => {
                  const percent = item.amount_limit ? Math.min((item.spent_amount / item.amount_limit) * 100, 100) : 0;
                  return `
                    <div class="stack-item">
                        <div class="stack-item-head">
                            <strong>${item.category_name}</strong>
                            <span>${currency.format(item.spent_amount)} / ${currency.format(item.amount_limit)}</span>
                        </div>
                        <p>${item.month}</p>
                        <div class="progress"><span style="width:${percent}%"></span></div>
                    </div>
                `;
              })
              .join("")
        : `<div class="stack-item"><p>No budgets created yet.</p></div>`;
}

function renderExpenseBreakdown(items) {
    const container = document.getElementById("expense-breakdown");
    if (!container) {
        return;
    }
    if (!items.length) {
        container.innerHTML = `<div class="stack-item"><p>No expenses recorded for this month.</p></div>`;
        return;
    }

    const highest = Math.max(...items.map((item) => Number(item.total)), 1);
    container.innerHTML = items
        .map(
            (item) => `
            <div class="stack-item">
                <div class="stack-item-head">
                    <strong>${item.category_name}</strong>
                    <span>${currency.format(item.total)}</span>
                </div>
                <div class="progress"><span style="width:${(item.total / highest) * 100}%"></span></div>
            </div>
        `
        )
        .join("");
}

function renderSummary(summary, activeMonth) {
    const activeMonthNode = document.getElementById("active-month");
    const totalBalanceNode = document.getElementById("total-balance");
    const monthlyIncomeNode = document.getElementById("monthly-income");
    const monthlyExpenseNode = document.getElementById("monthly-expense");
    const monthlyInvestmentNode = document.getElementById("monthly-investment");
    const netSavingsNode = document.getElementById("net-savings");
    if (activeMonthNode) activeMonthNode.textContent = activeMonth;
    if (totalBalanceNode) totalBalanceNode.textContent = currency.format(summary.total_balance);
    if (monthlyIncomeNode) monthlyIncomeNode.textContent = currency.format(summary.monthly_income);
    if (monthlyExpenseNode) monthlyExpenseNode.textContent = currency.format(summary.monthly_expense);
    if (monthlyInvestmentNode) monthlyInvestmentNode.textContent = currency.format(summary.monthly_investment || 0);
    if (netSavingsNode) netSavingsNode.textContent = currency.format(summary.net_savings);
}

async function loadReferenceData() {
    const [accountsData, categoriesData] = await Promise.all([api("/api/accounts"), api("/api/categories")]);
    state.accounts = accountsData.accounts;
    state.categories = categoriesData.categories;
    populateAccountOptions();
    populateCategoryOptions();
}

async function loadDashboard() {
    const dashboard = await api("/api/dashboard");
    renderSummary(dashboard.summary, dashboard.active_month);
    renderTransactions(dashboard.recent_transactions);
    renderBudgetProgress(dashboard.budget_progress);
    renderExpenseBreakdown(dashboard.expense_by_category);
}

async function refreshAll() {
    await loadReferenceData();
    await loadDashboard();
}

function formToJSON(form) {
    return Object.fromEntries(new FormData(form).entries());
}

async function attachSubmitHandler(formId, endpoint, successMessage) {
    const form = document.getElementById(formId);
    if (!form) {
        return;
    }
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        try {
            await api(endpoint, {
                method: "POST",
                body: JSON.stringify(formToJSON(form)),
            });
            form.reset();
            setDefaultDates();
            await refreshAll();
            showToast(successMessage);
        } catch (error) {
            showToast(error.message, true);
        }
    });
}

function setDefaultDates() {
    const transactionDate = document.getElementById("transaction-date");
    const budgetMonth = document.getElementById("budget-month");
    if (transactionDate) {
        transactionDate.valueAsDate = new Date();
    }
    if (budgetMonth) {
        budgetMonth.value = new Date().toISOString().slice(0, 7);
    }
}

function attachLoginHandler() {
    const form = document.getElementById("login-form");
    if (!form) {
        return;
    }
    form.addEventListener("submit", (event) => {
        event.preventDefault();
        showToast("Login successful");
        window.setTimeout(() => {
            window.location.href = "index.html";
        }, 600);
    });
}

function attachResetHandler() {
    const button = document.getElementById("reset-demo-button");
    if (!button) {
        return;
    }
    button.addEventListener("click", async () => {
        const confirmed = window.confirm("Reset all accounts, transactions, budgets, and categories to the clean default state?");
        if (!confirmed) {
            return;
        }
        try {
            await api("/api/reset", { method: "POST", body: JSON.stringify({}) });
            await refreshAll();
            showToast("Clean default data restored");
        } catch (error) {
            showToast(error.message, true);
        }
    });
}

async function init() {
    setDefaultDates();
    const transactionType = document.getElementById("transaction-type");
    if (transactionType) {
        transactionType.addEventListener("change", populateCategoryOptions);
    }
    attachLoginHandler();
    attachResetHandler();

    await Promise.all([
        attachSubmitHandler("transaction-form", "/api/transactions", "Transaction saved"),
        attachSubmitHandler("budget-form", "/api/budgets", "Budget saved"),
        attachSubmitHandler("account-form", "/api/accounts", "Account added"),
        attachSubmitHandler("category-form", "/api/categories", "Category added"),
    ]);

    try {
        await refreshAll();
        if (useLocalMode) {
            showToast("Offline demo mode active");
        }
    } catch (error) {
        showToast(error.message, true);
    }
}

init();
