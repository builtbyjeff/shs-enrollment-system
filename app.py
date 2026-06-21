from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'shs_enrollment_secret_key_2024'

DB_PATH = 'database.db'


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            middle_name TEXT,
            birth_date TEXT NOT NULL,
            gender TEXT NOT NULL,
            address TEXT NOT NULL,
            contact TEXT NOT NULL,
            guardian_name TEXT NOT NULL,
            guardian_contact TEXT NOT NULL,
            strand TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            school_year TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            enrolled_at TEXT NOT NULL
        )
    ''')

    # Insert default admin if not exists
    cursor.execute("SELECT * FROM admins WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO admins (username, password) VALUES ('admin', 'admin123')")

    conn.commit()
    conn.close()


def generate_student_id():
    conn = get_db()
    cursor = conn.cursor()
    year = datetime.now().year
    cursor.execute("SELECT COUNT(*) FROM students WHERE school_year LIKE ?", (f"{year}%",))
    count = cursor.fetchone()[0] + 1
    conn.close()
    return f"SHS-{year}-{count:04d}"


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        student_id = generate_student_id()
        enrolled_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            conn = get_db()
            conn.execute('''
                INSERT INTO students
                (student_id, first_name, last_name, middle_name, birth_date, gender,
                 address, contact, guardian_name, guardian_contact,
                 strand, grade_level, school_year, enrolled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                student_id,
                data['first_name'], data['last_name'], data.get('middle_name', ''),
                data['birth_date'], data['gender'],
                data['address'], data['contact'],
                data['guardian_name'], data['guardian_contact'],
                data['strand'], data['grade_level'], data['school_year'],
                enrolled_at
            ))
            conn.commit()
            conn.close()
            flash(f'Enrollment submitted! Your Student ID is {student_id}', 'success')
            return redirect(url_for('register'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username=? AND password=?", (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session['admin'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))


@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db()

    search = request.args.get('search', '')
    strand_filter = request.args.get('strand', '')
    status_filter = request.args.get('status', '')

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        query += " AND (first_name LIKE ? OR last_name LIKE ? OR student_id LIKE ?)"
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    if strand_filter:
        query += " AND strand = ?"
        params.append(strand_filter)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY enrolled_at DESC"
    students = conn.execute(query, params).fetchall()

    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM students WHERE status='Pending'").fetchone()[0]
    enrolled = conn.execute("SELECT COUNT(*) FROM students WHERE status='Enrolled'").fetchone()[0]
    rejected = conn.execute("SELECT COUNT(*) FROM students WHERE status='Rejected'").fetchone()[0]

    conn.close()

    return render_template('dashboard.html',
        students=students,
        total=total, pending=pending, enrolled=enrolled, rejected=rejected,
        search=search, strand_filter=strand_filter, status_filter=status_filter
    )


@app.route('/update_status/<int:student_id>', methods=['POST'])
def update_status(student_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    new_status = request.form['status']
    conn = get_db()
    conn.execute("UPDATE students SET status=? WHERE id=?", (new_status, student_id))
    conn.commit()
    conn.close()
    flash('Status updated.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if 'admin' not in session:
        return redirect(url_for('login'))

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    flash('Record deleted.', 'success')
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
