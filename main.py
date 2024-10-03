import sqlite3

# Helper function to connect to the database
def connect_db():
    return sqlite3.connect('student_data.db')

# Function to get data of a specific student
def get_student_data(student_name):
    conn = connect_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM students WHERE name = ?", (student_name,))
    student_data = c.fetchone()
    
    conn.close()
    return student_data

# Function to get student data by register number
def get_student_data_by_regno(reg_no):
    conn = connect_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM students WHERE reg_no = ?", (reg_no,))
    student_data = c.fetchone()
    
    conn.close()
    return student_data

# Function to allow student to edit selected details
def edit_student_data(student_name, allowed_fields):
    conn = connect_db()
    c = conn.cursor()
    
    student_data = get_student_data(student_name)
    if not student_data:
        print("Data not found.")
        return
    
    # Display existing data
    print(f"Existing Data for {student_name}:")
    print(student_data)
    
    # Allow editing
    for field in allowed_fields:
        new_value = input(f"Enter new {field}: ")
        c.execute(f"UPDATE students SET {field} = ? WHERE name = ?", (new_value, student_name))

    conn.commit()
    conn.close()

# Function for admin to view all student data
def view_all_data():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    
    all_data = c.fetchall()
    for student in all_data:
        print(student)
    
    conn.close()

# Function to add new student data
def add_new_student():
    conn = connect_db()
    c = conn.cursor()
    
    reg_no = input("Enter Register Number: ")
    name = input("Enter Name: ")
    department = input("Enter Department: ")
    year_perusing = int(input("Enter Year of Perusing: "))
    year_graduation = int(input("Enter Year of Graduation: "))
    contact_number = input("Enter Contact Number: ")
    email_id = input("Enter Email ID: ")
    cgpa = float(input("Enter CGPA: "))
    percentage = float(input("Enter Percentage: "))
    scholarship = input("Scholarship (y/n): ")
    fees_due = float(input("Enter Fees Due: "))
    
    c.execute('''INSERT INTO students (reg_no, name, department, year_perusing, year_graduation,
                contact_number, email_id, cgpa, percentage, scholarship, fees_due)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (reg_no, name, department, year_perusing, year_graduation, contact_number,
               email_id, cgpa, percentage, scholarship, fees_due))
    
    conn.commit()
    conn.close()
    print("New student data added successfully!")

# Function to delete student data
def delete_student_data():
    conn = connect_db()
    c = conn.cursor()
    
    reg_no = input("Enter Register Number of student to delete: ")
    c.execute("DELETE FROM students WHERE reg_no = ?", (reg_no,))
    
    conn.commit()
    conn.close()
    print(f"Data for student with Register Number {reg_no} deleted successfully.")

# Function to edit existing student data by admin
def admin_edit_student_data():
    reg_no = input("Enter Register Number of student to edit: ")
    student_data = get_student_data_by_regno(reg_no)
    
    if not student_data:
        print("Data not found.")
        return
    
    # Display data
    print(f"Existing Data for Register Number {reg_no}:")
    print(student_data)
    
    # Allow admin to edit any field
    columns = ["name", "department", "year_perusing", "year_graduation", "contact_number",
               "email_id", "cgpa", "percentage", "scholarship", "fees_due"]
    
    column = input(f"Which field do you want to edit? Options: {', '.join(columns)}: ")
    if column in columns:
        new_value = input(f"Enter new value for {column}: ")
        conn = connect_db()
        c = conn.cursor()
        c.execute(f"UPDATE students SET {column} = ? WHERE reg_no = ?", (new_value, reg_no))
        conn.commit()
        conn.close()
        print(f"Updated {column} successfully!")
    else:
        print("Invalid field selection.")

# Main program
def main():
    print("Starting application")
    
    user_type = input("Are you a student or admin? ").lower()
    
    if user_type == "student":
        student_name = input("Enter your name: ")
        student_data = get_student_data(student_name)
        
        if student_data:
            print(f"Data for {student_name}:")
            print(student_data)
            
            edit_choice = input("Do you want to edit your data? (yes/no): ").lower()
            if edit_choice == "yes":
                allowed_fields = ["name", "department", "year_perusing", "year_graduation",
                                  "contact_number", "email_id"]
                edit_student_data(student_name, allowed_fields)
            else:
                print("Closing data display.")
        
        else:
            print("Data not found. This event will be updated to admin.")
    
    elif user_type == "admin":
        password = input("Enter admin password: ")
        if password == "12345":
            while True:
                print("\nAdmin Menu:")
                print("1. View complete data")
                print("2. Add new student data")
                print("3. Edit existing student data")
                print("4. Delete a student data set")
                print("5. Quit the application")
                
                choice = input("Enter your choice: ")
                if choice == "1":
                    view_all_data()
                elif choice == "2":
                    add_new_student()
                elif choice == "3":
                    admin_edit_student_data()
                elif choice == "4":
                    delete_student_data()
                elif choice == "5":
                    print("Closing application.")
                    break
                else:
                    print("Invalid choice. Please try again.")
        else:
            print("Incorrect admin password.")
    
    else:
        print("Invalid user type. Please enter 'student' or 'admin'.")

if __name__ == "__main__":
    main()