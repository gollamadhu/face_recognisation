from collections import defaultdict
import csv
from flask import Flask, flash, render_template, Response, redirect, session, url_for, request,jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime,timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Pranay@964'

# Set session timeout to 30 minutes
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# # Define the User model for storing in the dataset
class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

users = [
    User(1, 'admin', 'password123')
]



path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)
for cl in myList:
    currentImage = cv2.imread(f'{path}/{cl}')
    images.append(currentImage)
    classNames.append(os.path.splitext(cl)[0])

attendance_tracker = {}
def denoise_image(image):
    if image is not None:
        # Apply a Gaussian blur to reduce noise (adjust parameters as needed)
        denoised_image = cv2.GaussianBlur(image, (5, 5), 0)
        return denoised_image
    else:
        return None
    
def calculate_individual_percentage(input_file='Attendance.csv', output_file='IndividualPercentage.csv'):
    # Read attendance data from the CSV file
    with open(input_file, 'r') as f:
        attendance_data = [line.strip().split(',') for line in f.readlines()]

    # Organize attendance data by student and month
    student_attendance = defaultdict(lambda: defaultdict(int))
    for entry in attendance_data[0:]:  # Skipping the header
        student_name, date,_ = entry
        month_year = '-'.join(date.split('-')[:2])  # Extract month and year
        student_attendance[student_name][month_year] += 1

    # Calculate individual percentage for each student and month
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        for student_name, month_data in student_attendance.items():
            for month, count in month_data.items():
                total_attendance_days = count
                total_percentage = (total_attendance_days / 30) * 100  # Assuming 30 days in a month
                writer.writerow([student_name, month, f'{total_percentage:.2f}'])

# Call the modified function to calculate individual percentages and write to the file
calculate_individual_percentage()


def markAttendance(name):
    today = datetime.now().strftime('%Y-%m-%d')
    now = datetime.now()
    dtString = now.strftime('%H:%M:%S')

    if name not in attendance_tracker:
        attendance_tracker[name] = {'dates': set(), 'entries': set()}

    if today not in attendance_tracker[name]['dates']:
        attendance_tracker[name]['dates'].add(today)

        # Check if the name and date combination is already present
        if (name, today) not in attendance_tracker[name]['entries']:
            attendance_tracker[name]['entries'].add((name, today))

            # Check if the entry already exists in the CSV file
            with open('Attendance.csv', 'r') as f:
                existing_entries = [line.strip().split(',') for line in f.readlines()]
                if (name, today) not in [(entry[0], entry[1]) for entry in existing_entries]:
                    # Update the CSV file with the new attendance data
                    with open('Attendance.csv', 'a+', newline='') as f:
                        writer = csv.writer(f)
                        # Check if the file is empty, write header if needed
                        if f.tell() == 0:
                            writer.writerow(['Name', 'Date', 'Time'])
                        writer.writerow([name, today, dtString])



       
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

encodeListKnown = findEncodings(images)

def gen_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        imgS = denoise_image(imgS)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                markAttendance(name)

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Flask-Login setup
@login_manager.user_loader
def load_user(user_id):
    return next((user for user in users if user.id == int(user_id)), None)

# Admin login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((user for user in users if user.username == username and user.password == password), None)
        if user:
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Incorrect username or password', 'error')
            session['show_popup'] = True
    return render_template('login.html')


@app.route('/admin')
@login_required
def admin():
    # Extend the session timeout each time the admin page is accessed
    session.permanent = True
    # Read attendance data from CSV file
    with open('Attendance.csv', 'r') as f:
        attendance_data = [line.strip().split(',') for line in f.readlines()]
        attendance_data = sorted(attendance_data, key=lambda x: x[1], reverse=True)

    # Filter by date if a date parameter is provided in the query string
    date_filter = request.args.get('date')
    if date_filter:
        attendance_data = [entry for entry in attendance_data if entry[1] == date_filter]

    # Check if the request wants JSON data
    if request.headers.get('Accept') == 'application/json':
        return jsonify(attendance_data)

    # Display attendance data in the admin UI
    return render_template('admin.html', username=current_user.username, attendance_data=attendance_data)

@app.route('/individual_percentage')
@login_required
def individual_percentage():
    # Read individual percentage data from CSV file
    with open('IndividualPercentage.csv', 'r') as f:
        individual_percentage_data = [line.strip().split(',') for line in f.readlines()]
        individual_percentage_data = sorted(individual_percentage_data, key=lambda x: x[0])

    # Get the selected date from the query parameters
    selected_date = request.args.get('date')

    # Filter the data based on the selected date
    if selected_date:
        filtered_data = [entry for entry in individual_percentage_data if entry[1] == selected_date]
    else:
        filtered_data = individual_percentage_data

    return render_template('individual_percentage.html', individual_percentage_data=filtered_data)

    # # Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True,host='localhost', port=2600)