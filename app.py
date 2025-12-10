# app.py
# Simple Expense Tracker (Flask + SQLite)


import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, flash

# Where the SQLite database file will be stored
DB_PATH = Path("data/expenses.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Helper to get a DB connection
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name
    return conn

# Create the table if it doesn't exist
def init_db():
    sql = """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    );
    """
    with get_conn() as conn:
        conn.execute(sql)

# Flask app setup
import os
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")  # used for flash messages (change in production)

with app.app_context():
    init_db()

# Home page — list all expenses
@app.route("/")
def index():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM expenses ORDER BY date DESC")
        rows = cur.fetchall()
    return render_template("index.html", expenses=rows)

# Add expense page (GET shows form, POST processes it)
@app.route("/add", methods=("GET", "POST"))
def add():
    if request.method == "POST":
        date = request.form.get("date", "").strip()
        amount = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip() or "Other"
        note = request.form.get("note", "").strip()

        # Basic validation
        if not date or not amount:
            flash("Date and amount are required.")
            return redirect(url_for("add"))
        try:
            # ensure amount can be converted to float
            float(amount)
        except ValueError:
            flash("Amount must be a number.")
            return redirect(url_for("add"))

        # Save to DB
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO expenses (date, amount, category, note, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
                (date, amount, category, note),
            )
        flash("Expense added.")
        return redirect(url_for("index"))

    # GET request: just show the form
    return render_template("add.html")

# Delete an expense (POST request from the list page)
@app.route("/delete/<int:eid>", methods=("POST",))
def delete(eid):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id = ?", (eid,))
    flash("Deleted.")
    return redirect(url_for("index"))

# Run the app when executed directly
if __name__ == "__main__":
    app.run(debug=True)



