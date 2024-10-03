import sqlite3

# Function to initialize the student database
def initialize_db():
    conn = sqlite3.connect('student_data.db')
    c = conn.cursor()
    
    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS students (
                    reg_no TEXT PRIMARY KEY,
                    name TEXT,
                    department TEXT,
                    year_joining INTEGER,
                    year_graduation INTEGER,
                    contact_number TEXT,
                    email_id TEXT,
                    cgpa REAL,
                    percentage REAL,
                    scholarship TEXT,
                    fees_due REAL
                )''')
    conn.commit()
    conn.close()

# Call this once when the program starts
initialize_db()
