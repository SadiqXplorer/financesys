import json
import sqlite3
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DB_PATH = BASE_DIR / "finance_manager.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'investment')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'investment')),
            amount REAL NOT NULL CHECK(amount > 0),
            note TEXT,
            transaction_date TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            month TEXT NOT NULL,
            amount_limit REAL NOT NULL CHECK(amount_limit > 0),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
            UNIQUE(user_id, category_id, month)
        );
        """
    )

    user = cursor.execute("SELECT id FROM users LIMIT 1").fetchone()
    if not user:
        cursor.execute(
            "INSERT INTO users (full_name, email) VALUES (?, ?)",
            ("SADIQ", "sadiq@example.com"),
        )
        user_id = cursor.lastrowid

        cursor.executemany(
            "INSERT INTO accounts (user_id, name, type, balance) VALUES (?, ?, ?, ?)",
            [
                (user_id, "Primary Bank", "Bank", 0),
                (user_id, "Cash Wallet", "Cash", 0),
            ],
        )

        cursor.executemany(
            "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)",
            [
                (user_id, "Salary", "income"),
                (user_id, "Freelance", "income"),
                (user_id, "Food", "expense"),
                (user_id, "Transport", "expense"),
                (user_id, "Bills", "expense"),
                (user_id, "Entertainment", "expense"),
                (user_id, "Mutual Fund", "investment"),
                (user_id, "Stocks", "investment"),
                (user_id, "Savings Deposit", "investment"),
            ],
        )

    conn.commit()
    conn.close()


def reset_db():
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def fetch_one_value(cursor, query, params=(), default=0):
    row = cursor.execute(query, params).fetchone()
    if row is None or row[0] is None:
        return default
    return row[0]


def json_response(handler, payload, status=200):
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler, message, status=400):
    json_response(handler, {"error": message}, status=status)


class FinanceRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/dashboard":
            self.handle_dashboard()
            return
        if parsed.path == "/api/accounts":
            self.handle_accounts_list()
            return
        if parsed.path == "/api/categories":
            self.handle_categories_list()
            return
        if parsed.path == "/api/transactions":
            self.handle_transactions_list(parsed.query)
            return
        if parsed.path == "/api/budgets":
            self.handle_budgets_list()
            return
        self.serve_static(parsed.path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/reset":
            self.handle_reset()
            return
        if parsed.path == "/api/accounts":
            self.handle_accounts_create()
            return
        if parsed.path == "/api/categories":
            self.handle_categories_create()
            return
        if parsed.path == "/api/transactions":
            self.handle_transactions_create()
            return
        if parsed.path == "/api/budgets":
            self.handle_budgets_create()
            return
        error_response(self, "Route not found", status=404)

    def log_message(self, format, *args):
        return

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw)

    def serve_static(self, path):
        requested = "index.html" if path in ("/", "") else path.lstrip("/")
        file_path = (STATIC_DIR / requested).resolve()
        if STATIC_DIR not in file_path.parents and file_path != STATIC_DIR / "index.html":
            error_response(self, "Invalid path", status=403)
            return
        if not file_path.exists() or not file_path.is_file():
            error_response(self, "File not found", status=404)
            return

        content_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
        }
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_types.get(file_path.suffix, "text/plain; charset=utf-8"))
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def handle_dashboard(self):
        conn = get_connection()
        cursor = conn.cursor()
        month = datetime.now().strftime("%Y-%m")

        total_balance = fetch_one_value(cursor, "SELECT SUM(balance) FROM accounts")
        monthly_income = fetch_one_value(cursor, "SELECT SUM(amount) FROM transactions WHERE type = 'income' AND substr(transaction_date, 1, 7) = ?", (month,))
        monthly_expense = fetch_one_value(cursor, "SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND substr(transaction_date, 1, 7) = ?", (month,))
        monthly_investment = fetch_one_value(cursor, "SELECT SUM(amount) FROM transactions WHERE type = 'investment' AND substr(transaction_date, 1, 7) = ?", (month,))

        recent_transactions = [
            dict(row)
            for row in cursor.execute(
                """
                SELECT t.id, t.type, t.amount, t.note, t.transaction_date,
                       a.name AS account_name, c.name AS category_name
                FROM transactions t
                JOIN accounts a ON a.id = t.account_id
                JOIN categories c ON c.id = t.category_id
                ORDER BY t.transaction_date DESC, t.id DESC
                LIMIT 6
                """
            ).fetchall()
        ]

        budget_progress = [
            dict(row)
            for row in cursor.execute(
                """
                SELECT b.id, b.month, b.amount_limit,
                       c.name AS category_name,
                       COALESCE(SUM(t.amount), 0) AS spent_amount
                FROM budgets b
                JOIN categories c ON c.id = b.category_id
                LEFT JOIN transactions t
                    ON t.category_id = b.category_id
                   AND t.type = 'expense'
                   AND substr(t.transaction_date, 1, 7) = b.month
                GROUP BY b.id, b.month, b.amount_limit, c.name
                ORDER BY c.name
                """
            ).fetchall()
        ]

        expense_by_category = [
            dict(row)
            for row in cursor.execute(
                """
                SELECT c.name AS category_name, ROUND(SUM(t.amount), 2) AS total
                FROM transactions t
                JOIN categories c ON c.id = t.category_id
                WHERE t.type = 'expense'
                  AND substr(t.transaction_date, 1, 7) = ?
                GROUP BY c.name
                ORDER BY total DESC
                """,
                (month,),
            ).fetchall()
        ]

        conn.close()
        json_response(
            self,
            {
                "summary": {
                    "total_balance": round(total_balance, 2),
                    "monthly_income": round(monthly_income, 2),
                    "monthly_expense": round(monthly_expense, 2),
                    "monthly_investment": round(monthly_investment, 2),
                    "net_savings": round(monthly_income - monthly_expense - monthly_investment, 2),
                },
                "recent_transactions": recent_transactions,
                "budget_progress": budget_progress,
                "expense_by_category": expense_by_category,
                "active_month": month,
            },
        )

    def handle_accounts_list(self):
        conn = get_connection()
        rows = conn.execute("SELECT id, name, type, balance, created_at FROM accounts ORDER BY id DESC").fetchall()
        conn.close()
        json_response(self, {"accounts": [dict(row) for row in rows]})

    def handle_accounts_create(self):
        data = self.read_json()
        name = str(data.get("name", "")).strip()
        account_type = str(data.get("type", "")).strip()
        balance = data.get("balance", 0)
        if not name or not account_type:
            error_response(self, "Account name and type are required")
            return
        try:
            balance = float(balance)
        except (TypeError, ValueError):
            error_response(self, "Balance must be a valid number")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO accounts (user_id, name, type, balance) VALUES (?, ?, ?, ?)", (1, name, account_type, balance))
        conn.commit()
        created = conn.execute("SELECT id, name, type, balance, created_at FROM accounts WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        json_response(self, {"account": dict(created)}, status=201)

    def handle_categories_list(self):
        conn = get_connection()
        rows = conn.execute("SELECT id, name, type FROM categories ORDER BY type, name").fetchall()
        conn.close()
        json_response(self, {"categories": [dict(row) for row in rows]})

    def handle_categories_create(self):
        data = self.read_json()
        name = str(data.get("name", "")).strip()
        category_type = str(data.get("type", "")).strip().lower()
        if not name or category_type not in {"income", "expense", "investment"}:
            error_response(self, "Category name and a valid type are required")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?)", (1, name, category_type))
        conn.commit()
        created = conn.execute("SELECT id, name, type FROM categories WHERE id = ?", (cursor.lastrowid,)).fetchone()
        conn.close()
        json_response(self, {"category": dict(created)}, status=201)

    def handle_transactions_list(self, query_string):
        query = parse_qs(query_string)
        transaction_type = query.get("type", [""])[0].strip().lower()

        sql = """
            SELECT t.id, t.type, t.amount, t.note, t.transaction_date,
                   a.name AS account_name, c.name AS category_name
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            JOIN categories c ON c.id = t.category_id
        """
        params = []
        if transaction_type in {"income", "expense"}:
            sql += " WHERE t.type = ?"
            params.append(transaction_type)
        sql += " ORDER BY t.transaction_date DESC, t.id DESC"

        conn = get_connection()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        json_response(self, {"transactions": [dict(row) for row in rows]})

    def handle_transactions_create(self):
        data = self.read_json()
        for field in ["account_id", "category_id", "type", "amount", "transaction_date"]:
            if field not in data or str(data[field]).strip() == "":
                error_response(self, f"{field} is required")
                return

        transaction_type = str(data["type"]).strip().lower()
        if transaction_type not in {"income", "expense", "investment"}:
            error_response(self, "Transaction type must be income, expense, or investment")
            return
        try:
            amount = float(data["amount"])
        except (TypeError, ValueError):
            error_response(self, "Amount must be a valid number")
            return
        if amount <= 0:
            error_response(self, "Amount must be greater than 0")
            return

        conn = get_connection()
        cursor = conn.cursor()
        account = cursor.execute("SELECT id FROM accounts WHERE id = ?", (data["account_id"],)).fetchone()
        category = cursor.execute("SELECT id, type FROM categories WHERE id = ?", (data["category_id"],)).fetchone()
        if not account or not category:
            conn.close()
            error_response(self, "Selected account or category does not exist")
            return
        if category["type"] != transaction_type:
            conn.close()
            error_response(self, "Category type must match transaction type")
            return

        cursor.execute(
            """
            INSERT INTO transactions
            (user_id, account_id, category_id, type, amount, note, transaction_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (1, data["account_id"], data["category_id"], transaction_type, amount, str(data.get("note", "")).strip(), str(data["transaction_date"]).strip()),
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount if transaction_type == "income" else -amount, data["account_id"]),
        )
        conn.commit()
        created = conn.execute(
            """
            SELECT t.id, t.type, t.amount, t.note, t.transaction_date,
                   a.name AS account_name, c.name AS category_name
            FROM transactions t
            JOIN accounts a ON a.id = t.account_id
            JOIN categories c ON c.id = t.category_id
            WHERE t.id = ?
            """,
            (cursor.lastrowid,),
        ).fetchone()
        conn.close()
        json_response(self, {"transaction": dict(created)}, status=201)

    def handle_budgets_list(self):
        conn = get_connection()
        rows = conn.execute(
            """
            SELECT b.id, b.month, b.amount_limit, c.name AS category_name, c.id AS category_id
            FROM budgets b
            JOIN categories c ON c.id = b.category_id
            ORDER BY b.month DESC, c.name
            """
        ).fetchall()
        conn.close()
        json_response(self, {"budgets": [dict(row) for row in rows]})

    def handle_budgets_create(self):
        data = self.read_json()
        month = str(data.get("month", "")).strip()
        category_id = data.get("category_id")
        amount_limit = data.get("amount_limit")
        if not month or not category_id:
            error_response(self, "Month and category are required")
            return
        try:
            amount_limit = float(amount_limit)
        except (TypeError, ValueError):
            error_response(self, "Budget amount must be a valid number")
            return
        if amount_limit <= 0:
            error_response(self, "Budget amount must be greater than 0")
            return

        conn = get_connection()
        cursor = conn.cursor()
        category = cursor.execute("SELECT id, type FROM categories WHERE id = ?", (category_id,)).fetchone()
        if not category:
            conn.close()
            error_response(self, "Category not found")
            return
        if category["type"] != "expense":
            conn.close()
            error_response(self, "Budgets can only be created for expense categories")
            return

        cursor.execute(
            """
            INSERT INTO budgets (user_id, category_id, month, amount_limit)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, category_id, month)
            DO UPDATE SET amount_limit = excluded.amount_limit
            """,
            (1, category_id, month, amount_limit),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT b.id, b.month, b.amount_limit, c.name AS category_name, c.id AS category_id
            FROM budgets b
            JOIN categories c ON c.id = b.category_id
            WHERE b.user_id = ? AND b.category_id = ? AND b.month = ?
            """,
            (1, category_id, month),
        ).fetchone()
        conn.close()
        json_response(self, {"budget": dict(row)}, status=201)

    def handle_reset(self):
        reset_db()
        json_response(self, {"message": "Demo data restored successfully"})


def run():
    init_db()
    server = HTTPServer(("127.0.0.1", 8000), FinanceRequestHandler)
    print("Finance Management System running at http://127.0.0.1:8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
