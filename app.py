import logging
import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import sqlite3
import gspread
from google.oauth2.service_account import Credentials

from main import get_student_data

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Helper function to connect to the database
def connect_db():
    try:
        conn = sqlite3.connect('student_data.db')
        return conn
    except sqlite3.Error as e:
        logging.error("Database connection error: %s", e)
        return None

# Function to fetch edit requests from Google Sheets
def fetch_edit_requests():
    try:
        logging.debug("Fetching edit requests from Google Sheets")
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if not os.path.exists(credentials_path):
            logging.error("Credentials file not found. Please ensure 'credentials.json' is in the correct path.")
            return []
        creds = Credentials.from_service_account_file(credentials_path, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open("Student Edit Requests").sheet1
        logging.debug("Successfully fetched edit requests")
        return sheet.get_all_records()
    except Exception as e:
        logging.error("Error fetching edit requests: %s", e)
        return []

# Route to serve static files
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Route to display the home page
@app.route('/')
def home():
    return render_template('index.html', css_file=url_for('send_static', path='styles.css'))

# Route to handle student login
@app.route('/student', methods=['POST'])
def student():
    student_name = request.form['name']
    student_data = get_student_data(student_name)
    if student_data:
        return render_template('student.html', student_data=student_data, css_file=url_for('send_static', path='styles.css'))
    else:
        # Log the event for admin notification
        logging.info("Student data not found for: %s", student_name)
        with open('student_not_found.log', 'a') as f:
            f.write(f"Student data not found for: {student_name}\n")
        # Render the student not found page
        return render_template('student_not_found.html', css_file=url_for('send_static', path='styles.css'))

# Route to handle admin login
@app.route('/admin', methods=['POST'])
def admin():
    password = request.form['password']
    if password == "12345":
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        return "Incorrect admin password."

# Route to display admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_logged_in' in session:
        try:
            edit_requests = fetch_edit_requests()
            return render_template('admin.html', css_file=url_for('send_static', path='styles.css'), edit_requests=edit_requests)
        except Exception as e:
            logging.error("Error fetching edit requests: %s", e)
            return "An error occurred while fetching edit requests."
    else:
        return redirect(url_for('home'))

# Route to approve edit request
@app.route('/approve_edit/<int:request_id>', methods=['POST'])
def approve_edit(request_id):
    edit_requests = fetch_edit_requests()
    if not edit_requests:
        return "Failed to fetch edit requests."
    request_data = edit_requests[request_id]
    register_number = request_data['Register Number']
    contact_number = request_data['New Contact Number']
    email_id = request_data['New Email ID']
    conn = connect_db()
    if conn:
        c = conn.cursor()
        c.execute("UPDATE students SET contact_number = ?, email_id = ? WHERE register_number = ?", (contact_number, email_id, register_number))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    else:
        return "Database connection error."

# Route to handle admin logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home'))

# Route to view all student data (admin)
@app.route('/view_all')
def view_all():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    all_data = c.fetchall()
    conn.close()
    return render_template('view_all.html', all_data=all_data, css_file=url_for('send_static', path='styles.css'))

# Route to add new student data (admin)
@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # Extract student data from the form
        register_number = request.form['register_number']
        name = request.form['name']
        contact_number = request.form['contact_number']
        email_id = request.form['email_id']
        # Insert the new student data into the database
        conn = connect_db()
        if conn:
            c = conn.cursor()
            c.execute("INSERT INTO students (register_number, name, contact_number, email_id) VALUES (?, ?, ?, ?)",
                      (register_number, name, contact_number, email_id))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            return "Database connection error."
    else:
        return render_template('add_student.html', css_file=url_for('send_static', path='styles.css'))

# Route to edit student data (admin)
@app.route('/edit_student_admin', methods=['GET', 'POST'])
def edit_student_admin():
    if request.method == 'POST':
        # Extract student data from the form
        register_number = request.form['register_number']
        contact_number = request.form['contact_number']
        email_id = request.form['email_id']
        # Update the student data in the database
        conn = connect_db()
        if conn:
            c = conn.cursor()
            c.execute("UPDATE students SET contact_number = ?, email_id = ? WHERE register_number = ?",
                      (contact_number, email_id, register_number))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            return "Database connection error."
    else:
        return render_template('edit_student_admin.html', css_file=url_for('send_static', path='styles.css'))

# Route to delete student data (admin)
@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        # Extract register number from the form
        register_number = request.form['register_number']
        # Delete the student data from the database
        conn = connect_db()
        if conn:
            c = conn.cursor()
            c.execute("DELETE FROM students WHERE register_number = ?", (register_number,))
            conn.commit()
            conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            return "Database connection error."
    else:
        return render_template('delete_student.html', css_file=url_for('send_static', path='styles.css'))

# Route to edit student personal details
@app.route('/edit_student_personal/<register_number>', methods=['GET', 'POST'])
def edit_student_personal(register_number):
    if request.method == 'POST':
        contact_number = request.form['contact_number']
        email_id = request.form['email_id']
        conn = connect_db()
        c = conn.cursor()
        c.execute("UPDATE students SET contact_number = ?, email_id = ? WHERE register_number = ?", (contact_number, email_id, register_number))
        conn.commit()
        conn.close()
        return redirect(url_for('student', name=register_number))
    else:
        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE register_number = ?", (register_number,))
        student_data = c.fetchone()
        conn.close()
        return render_template('edit_student.html', student_data=student_data, css_file=url_for('send_static', path='styles.css'))

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logging.error("Error starting the Flask application: %s", e)
        raise

        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logging.error("Error starting the Flask application: %s", e)
        raise
