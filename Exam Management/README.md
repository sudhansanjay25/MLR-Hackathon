# Exam Management System

Unified Exam Management System built with Flask and MongoDB.

## Prerequisites
- Python 3.x
- MongoDB (Running locally on default port 27017)

## Installation

1. Create a virtual environment (if not already in `ht` or similar):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup Mock Data

Before running the application, populate the database with mock data (Students, Departments, Subjects, Users):

```bash
python seed_data.py
```
*Note: This will clear existing data in the `exam_management_system` database and re-seed it.*

## Running the Application

```bash
python app.py
```

Access the application at: [http://localhost:5000](http://localhost:5000)

## Default Credentials

### COE (Controller of Exams)
- Email: `coe@mlrit.ac.in`
- Password: `coe123`

### Faculty
- Email: `faculty001@mlrit.ac.in`
- Password: `faculty123`

### Student
- Email: `714025104001@mlrit.ac.in`
- Password: `student123`
*(Note: Student ID `7140...` is generated dynamically in `seed_data.py`, check the console output of seed script or MongoDB if this specific ID doesn't work, but the logic tries to create predictable IDs).*

## Workflows

1. **COE**: Login -> Schedule Exam -> View Schedule -> Generate Seating -> Authorize Hall Ticket.
2. **Student**: Login -> Download Hall Ticket (if authorized).
3. **Faculty**: Login -> Scan QR (Simulate by entering Reg No) -> Mark Attendance.
