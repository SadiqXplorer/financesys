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

async function api(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Request failed");
    }
    return data;
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
                  const percent = Math.min((item.spent_amount / item.amount_limit) * 100, 100);
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

    const highest = Math.max(...items.map((item) => Number(item.total)));
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
    } catch (error) {
        showToast(error.message, true);
    }
}

init();
