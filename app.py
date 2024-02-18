from flask import Flask, render_template, request, redirect, flash, url_for, session
import pymongo
from datetime import datetime
# from attendance import Attendance  # Assuming attendance.py contains the Attendance class


app = Flask(__name__, static_url_path='/student_management/static')
app = Flask(__name__)
app.secret_key = '136-287-262'

# MongoDB Connection
client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["attendance_db"]
students_collection = db["students"]
attendance_collection = db["attendance"]

def is_logged_in():
    return 'username' in session  # Assuming the username is stored in the session upon login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password =='admin':
            session['username'] = username  # Store username in session upon successful login
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')
    
# Route to handle logout
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session upon logout
    return redirect(url_for('index'))

# Decorator to restrict access to routes if not logged in
@app.before_request
def require_login():
    allowed_routes = ['index', 'login', 'static']  # List of routes allowed without login
    if request.endpoint not in allowed_routes and not is_logged_in():
        flash('You must be logged in to access this page', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/attendance')
def show_attendance():
    all_students = students_collection.find()
    return render_template('attendance.html', students=all_students)

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    roll_number = request.form['roll_number']
    student = students_collection.find_one({"roll_number": roll_number})
    if student :
        student_name = student["name"]
        current_date = datetime.now().strftime("%Y-%m-%d")
        existing_record = attendance_collection.find_one({"name": student_name, "date": current_date})
        if existing_record:
            flash('Attendance for this student has already been marked today.', 'info')
        else:
            attendance_data = {
                "name": student_name,
                "roll_number": roll_number,
                "date": current_date,
                "status": "Present"
            }
            attendance_collection.insert_one(attendance_data)
            flash('Attendance marked successfully for the student.', 'success')
    else:
        flash('No student found with this roll number.', 'error')
    return redirect('/attendance')

@app.route('/add_student', methods=['POST', 'GET'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        department = request.form.get('department')

        if not (name and roll_number and department):
            flash('Please provide all required information.', 'error')
            return redirect('/dashboard')

        existing_student = students_collection.find_one({"roll_number": roll_number})
        if existing_student:
            flash('A student with this roll number already exists.', 'error')
        else:
            student_data = {
                "name": name,
                "roll_number": roll_number,
                "department": department
            }
            students_collection.insert_one(student_data)
            
            flash('Student added successfully.', 'success')

    return render_template('add_student.html')


@app.route('/delete_student', methods=['POST', 'GET', 'DELETE'])
def delete_student():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')

        if not roll_number:
            flash('Please provide the roll number of the student to delete.', 'error')
        else:
            existing_student = students_collection.find_one({"roll_number": roll_number})
            if existing_student:
                students_collection.delete_one({"roll_number": roll_number})
                flash('Student deleted successfully.', 'success')
            else:
                flash('No student found with this roll number.', 'error')

    return render_template('delete_student.html')

@app.route('/update_student', methods=['POST', 'GET'])
def update_student():
    if request.method == 'POST':
        roll_number = request.form.get('roll_number')
        new_name = request.form.get('new_name')
        new_department = request.form.get('new_department')

        if not (roll_number and new_name and new_department):
            flash('Please provide all required information.', 'error')
        else:
            existing_student = students_collection.find_one({"roll_number": roll_number})
            if existing_student:
                students_collection.update_one({"roll_number": roll_number}, {"$set": {"name": new_name, "department": new_department}})
                flash('Student information updated successfully.', 'success')
            else:
                flash('No student found with this roll number.', 'error')

    return render_template('update_student.html')



# Route to render the attendance list template

@app.route('/attendance_list')
def attendance_list():
    # Fetch attendance data from the MongoDB database
    attendance_data = list(attendance_collection.find())
    return render_template('attendance_list.html', attendance_list=attendance_data)



if __name__ == '__main__':
    app.run(debug=True)



