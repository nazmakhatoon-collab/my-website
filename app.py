from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pyq (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            year TEXT,
            semester TEXT,
            filename TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------- ROUTES ----------------

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Library + Search
@app.route('/library', methods=['GET', 'POST'])
def library():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    subject = request.form.get('subject')
    year = request.form.get('year')
    semester = request.form.get('semester')

    query = "SELECT * FROM pyq WHERE 1=1"
    params = []

    if subject:
        query += " AND subject LIKE ?"
        params.append(f"%{subject}%")

    if year:
        query += " AND year LIKE ?"
        params.append(f"%{year}%")

    if semester:
        query += " AND semester LIKE ?"
        params.append(f"%{semester}%")

    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()

    return render_template('index.html', data=data)

# Admin Upload
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        subject = request.form['subject']
        year = request.form['year']
        semester = request.form['semester']
        file = request.files['file']

        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO pyq VALUES (NULL, ?, ?, ?, ?)",
                (subject, year, semester, filename)
            )
            conn.commit()
            conn.close()

        return redirect(url_for('admin'))

    return render_template('admin.html')

# Download
@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
