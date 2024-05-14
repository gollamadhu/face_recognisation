Objectives:

•	Face Recognition for Attendance
•	Web-Based User Interface
•	User Authentication
•	Admin Dashboard
•	Date Filtering
•	Individual Percentage Calculation
•	CSV File Handling
•	Session Management
•	Logout Functionality
•	Webcam Video Feed
•	Styling and UI



Libraries Used:

cv2 -OpenCV, a popular computer vision library.
Flask-A web framework for building web applications in Python.
Flask-Login-An extension for Flask that provides user session management.
numpy -used for numerical operations. 
face_recognition- library for face recognition,
os - used for working with the operating system.
Datetime - is used for working with date and time.
DefaultDict-A dictionary subclass from the collections module that returns a default value when a key is not found.
CSV-A module for reading and writing CSV files.


Functions Explanation:

calculate_individual_percentage:
•	Reads attendance data from a CSV file.
•	Organizes attendance data by student and date.
•	Calculates individual percentage for each student for each month.
•	Writes the calculated percentages to a new CSV file.
markAttendance:
•	Takes the name of a recognized face and marks the attendance.
•	Uses the current date and time to record attendance.
•	Updates a dictionary (attendance_tracker) with attendance information.
findEncodings:
•	Takes a list of images containing faces.
•	Uses face_recognition library to find face encodings for each image.
•	Returns a list of face encodings.
gen_frames:
•	Captures frames from the webcam using OpenCV.
•	Applies face recognition to identify faces in the frames.
•	Marks attendance for recognized faces.
•	Streams processed frames as JPEG images for a video feed.
index:
•	Renders the main index page of the Flask app.
video_feed:
Returns a video feed response using the gen_frames function.
login:
•	Handles user login functionality.
•	Checks username and password against predefined user data.
•	Redirects to the admin page upon successful login.
admin:
•	Renders the admin dashboard.
•	Reads attendance data from a CSV file.
•	Optionally filters data based on the provided date parameter.
•	Displays attendance data in a table format.
individual_percentage:
•	Renders the individual percentage page.
•	Reads individual percentage data from a CSV file.
•	Optionally filters data based on the selected date.
•	Displays individual percentages in a table format.
logout:
•	Logs out the current user and redirects to the login page.

