import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Retry logic to wait for the PostgreSQL container to be ready
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            # We connect to 'db' (the service name in docker-compose), NOT localhost
            conn = psycopg2.connect(
                host='db',
                database=os.environ.get('DB_NAME', 'todo_db'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres')
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database not ready. Retrying... ({5 - retries}/5)")
            time.sleep(3)
    raise Exception("Could not connect to the database")

# Initialize the database table
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title VARCHAR(150) NOT NULL,
            completed BOOLEAN DEFAULT FALSE
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks ORDER BY id DESC;')
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO tasks (title) VALUES (%s);', (title,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    # Run on port 5000, accessible outside the container
    app.run(host='0.0.0.0', port=5000)
