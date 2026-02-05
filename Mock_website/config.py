# Configuration for Exam Management System
from pymongo import MongoClient
import os

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "exam_management_system"

# Flask Configuration
SECRET_KEY = "mock_secret_key_for_exam_system"

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Default Password for all users
DEFAULT_PASSWORD = "password123"

# Departments
DEPARTMENTS = [101, 201, 301, 401, 501]

# Years and their joining years
YEAR_MAPPING = {
    1: 25,  # 2025
    2: 24,  # 2024
    3: 23,  # 2023
    4: 22   # 2022
}

# Semesters per year
SEMESTER_MAPPING = {
    1: {"odd": 1, "even": 2},
    2: {"odd": 3, "even": 4},
    3: {"odd": 5, "even": 6},
    4: {"odd": 7, "even": 8}
}

# Subject Classifications
SUBJECT_TYPES = ["HEAVY", "NONMAJOR"]

# Exam Types
EXAM_TYPES = ["Internal 1", "Internal 2", "Semester"]

# Session Types
SESSIONS = ["FN", "AN"]  # Forenoon, Afternoon

# Session timings (matching your original format)
SESSION_TIMINGS = {
    'FN': '10:00 AM - 1:00 PM',
    'AN': '2:00 PM - 5:00 PM',
    'FN_INTERNAL': '9:00 AM - 10:30 AM',
    'AN_INTERNAL': '2:00 PM - 3:30 PM'
}

# Hall Configuration
TOTAL_HALLS = 20
MIN_BENCH_CAPACITY = 30
MAX_BENCH_CAPACITY = 35
MIN_COLUMNS = 4
MAX_COLUMNS = 6

# Students per department per year
STUDENTS_PER_DEPT_PER_YEAR = 100

# Total Faculty
TOTAL_FACULTY = 20

# QR Scan Time Window (in minutes)
QR_SCAN_WINDOW_BEFORE = 30
QR_SCAN_WINDOW_AFTER = 30

# PDF Storage Path (absolute)
PDF_STORAGE_PATH = os.path.join(BASE_DIR, "seating_pdfs")
HALL_TICKET_STORAGE_PATH = os.path.join(BASE_DIR, "hall_tickets")

# Default student photo path
DEFAULT_STUDENT_PHOTO = "static/default_student.png"

def get_db():
    """Get MongoDB database connection"""
    client = MongoClient(MONGO_URI)
    return client[DATABASE_NAME]
