from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
import time

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'expense_database'),
    'user': os.environ.get('DB_USER', 'expense_user'),
    'password': os.environ.get('DB_PASSWORD', 'expense_pass'),
    'database': os.environ.get('DB_NAME', 'expense_db')
}


def get_db_connection():
    """Create and return a database connection."""
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    """Initialize the database table if it doesn't exist."""
    max_retries = 30
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    description VARCHAR(255) NOT NULL,
                    category VARCHAR(100) NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    expense_date DATE NOT NULL
                )
            ''')
            conn.commit()
            cursor.close()
            conn.close()
            print("Database initialized successfully.")
            return
        except mysql.connector.Error as err:
            print(f"Attempt {attempt + 1}/{max_retries}: Database not ready - {err}")
            time.sleep(2)
    print("Failed to connect to database after maximum retries.")


@app.route('/')
def index():
    """Display all expenses and the total."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM expenses ORDER BY expense_date DESC')
    expenses = cursor.fetchall()
    cursor.execute('SELECT COALESCE(SUM(amount), 0) AS total FROM expenses')
    total = cursor.fetchone()['total']
    cursor.close()
    conn.close()
    return render_template('index.html', expenses=expenses, total=total)


@app.route('/add', methods=['POST'])
def add_expense():
    """Add a new expense."""
    description = request.form['description']
    category = request.form['category']
    amount = request.form['amount']
    expense_date = request.form['expense_date']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO expenses (description, category, amount, expense_date) VALUES (%s, %s, %s, %s)',
        (description, category, float(amount), expense_date)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """Delete an expense by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM expenses WHERE id = %s', (expense_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
