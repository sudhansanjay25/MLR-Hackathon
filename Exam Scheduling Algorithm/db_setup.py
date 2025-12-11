"""
Database setup for Exam Scheduling System
Creates tables and populates with mock data
"""

import sqlite3
from datetime import datetime, timedelta

def create_database():
    """Create database and all required tables"""
    conn = sqlite3.connect('exam_scheduling.db')
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS schedule_violations')
    cursor.execute('DROP TABLE IF EXISTS exam_schedule')
    cursor.execute('DROP TABLE IF EXISTS holidays')
    cursor.execute('DROP TABLE IF EXISTS exam_cycles')
    cursor.execute('DROP TABLE IF EXISTS subjects')
    cursor.execute('DROP TABLE IF EXISTS students')
    
    # Create Students table
    cursor.execute('''
    CREATE TABLE students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        roll_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL
    )
    ''')
    
    # Create Subjects table
    cursor.execute('''
    CREATE TABLE subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT NOT NULL,
        subject_name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        subject_type TEXT NOT NULL,
        exam_type TEXT NOT NULL,
        credits INTEGER,
        duration REAL,
        student_count INTEGER DEFAULT 0
    )
    ''')
    
    # Create Exam Cycles table
    cursor.execute('''
    CREATE TABLE exam_cycles (
        cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_type TEXT NOT NULL,
        year_group INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_date TEXT NOT NULL,
        status TEXT DEFAULT 'PENDING'
    )
    ''')
    
    # Create Holidays table
    cursor.execute('''
    CREATE TABLE holidays (
        holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER,
        holiday_date TEXT NOT NULL,
        reason TEXT,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id)
    )
    ''')
    
    # Create Exam Schedule table
    cursor.execute('''
    CREATE TABLE exam_schedule (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        department TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        session TEXT NOT NULL,
        student_count INTEGER,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    # Create Constraint Violations Log table
    cursor.execute('''
    CREATE TABLE schedule_violations (
        violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        violation_type TEXT NOT NULL,
        description TEXT,
        severity TEXT,
        FOREIGN KEY (exam_cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    conn.commit()
    return conn

def populate_mock_data(conn):
    """Populate database with realistic mock data"""
    cursor = conn.cursor()
    
    # Insert mock students (60 students across 3 departments, Year 2)
    students_data = []
    departments = ['CSE', 'ECE', 'MECH']
    
    for dept in departments:
        for i in range(1, 21):  # 20 students per department
            roll_num = f"{dept}2023{i:03d}"
            name = f"Student_{dept}_{i}"
            students_data.append((roll_num, name, dept, 2, 3))  # Year 2, Semester 3
    
    cursor.executemany('''
    INSERT INTO students (roll_number, name, department, year, semester)
    VALUES (?, ?, ?, ?, ?)
    ''', students_data)
    
    # Insert mock subjects for Year 2, Semester 3
    subjects_data = [
        # CSE Subjects
        ('CS301', 'Data Structures', 'CSE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS302', 'Computer Organization', 'CSE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS303', 'Discrete Mathematics', 'CSE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS304', 'Operating Systems', 'CSE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS305', 'Database Systems', 'CSE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('CS306', 'Software Engineering', 'CSE', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS307', 'Web Technologies', 'CSE', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('CS308', 'Computer Networks Lab', 'CSE', 2, 3, 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # ECE Subjects
        ('EC301', 'Signals and Systems', 'ECE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC302', 'Digital Electronics', 'ECE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC303', 'Electronic Devices', 'ECE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC304', 'Control Systems', 'ECE', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('EC305', 'Communication Systems', 'ECE', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC306', 'Microprocessors', 'ECE', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('EC307', 'Circuit Simulation Lab', 'ECE', 2, 3, 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
        
        # MECH Subjects
        ('ME301', 'Thermodynamics', 'MECH', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME302', 'Fluid Mechanics', 'MECH', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME303', 'Machine Design', 'MECH', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME304', 'Manufacturing Processes', 'MECH', 2, 3, 'HEAVY', 'BOTH', 4, 3.0, 20),
        ('ME305', 'Material Science', 'MECH', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME306', 'Engineering Drawing', 'MECH', 2, 3, 'NONMAJOR', 'BOTH', 3, 3.0, 20),
        ('ME307', 'Workshop Practice', 'MECH', 2, 3, 'NONMAJOR', 'INTERNAL', 2, 1.5, 20),
    ]
    
    cursor.executemany('''
    INSERT INTO subjects (subject_code, subject_name, department, year, semester, 
                         subject_type, exam_type, credits, duration, student_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', subjects_data)
    
    conn.commit()
    print("✅ Database created and populated with mock data")
    print(f"   - {len(students_data)} students added")
    print(f"   - {len(subjects_data)} subjects added")

def print_database_summary(conn):
    """Print summary of database contents"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("DATABASE SUMMARY")
    print("="*60)
    
    # Students summary
    cursor.execute('SELECT department, COUNT(*) FROM students GROUP BY department')
    print("\n📚 Students by Department:")
    for dept, count in cursor.fetchall():
        print(f"   {dept}: {count} students")
    
    # Subjects summary
    cursor.execute('''
    SELECT department, subject_type, COUNT(*) 
    FROM subjects 
    WHERE exam_type IN ('SEMESTER', 'BOTH')
    GROUP BY department, subject_type
    ''')
    print("\n📖 Semester Exam Subjects:")
    current_dept = None
    for dept, stype, count in cursor.fetchall():
        if dept != current_dept:
            print(f"   {dept}:")
            current_dept = dept
        print(f"      {stype}: {count} subjects")
    
    cursor.execute('''
    SELECT department, COUNT(*) 
    FROM subjects 
    WHERE exam_type = 'INTERNAL' OR exam_type = 'BOTH'
    GROUP BY department
    ''')
    print("\n📝 Internal Exam Subjects:")
    for dept, count in cursor.fetchall():
        print(f"   {dept}: {count} subjects")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("Creating Exam Scheduling Database...")
    conn = create_database()
    populate_mock_data(conn)
    print_database_summary(conn)
    conn.close()
    print("\n✅ Database setup complete! File: exam_scheduling.db")
