"""
Integrated Database Setup for All Three Modules:
1. Exam Scheduling
2. Seating Allocation
3. Hall Ticket Generation

This script creates tables and populates mock data in exam_scheduling.db
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'exam_scheduling.db')

def create_tables(conn):
    """Create all necessary tables for the integrated system"""
    cursor = conn.cursor()
    
    # =================================================================
    # EXISTING TABLES (From Exam Scheduling)
    # =================================================================
    
    # Subjects table (already exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_code TEXT UNIQUE NOT NULL,
        subject_name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester_type TEXT NOT NULL,
        subject_type TEXT NOT NULL,
        exam_type TEXT NOT NULL,
        student_count INTEGER DEFAULT 0
    )
    ''')
    
    # Exam cycles table (already exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exam_cycles (
        cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_type TEXT NOT NULL,
        year_group INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        created_date TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Schedules table (already exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        exam_date TEXT NOT NULL,
        session TEXT NOT NULL,
        FOREIGN KEY (cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    # Schedule violations table (already exists)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule_violations (
        violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        violation_type TEXT NOT NULL,
        description TEXT,
        severity TEXT DEFAULT 'MEDIUM',
        FOREIGN KEY (cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')
    
    # =================================================================
    # NEW TABLES (For Seating Allocation)
    # =================================================================
    
    # Halls table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS halls (
        hall_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hall_name TEXT UNIQUE NOT NULL,
        capacity INTEGER NOT NULL,
        columns INTEGER NOT NULL,
        active INTEGER DEFAULT 1
    )
    ''')
    
    # Teachers/Invigilators table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_name TEXT NOT NULL,
        department TEXT,
        contact TEXT,
        active INTEGER DEFAULT 1
    )
    ''')
    
    # Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        reg_no TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year INTEGER NOT NULL,
        semester INTEGER NOT NULL,
        degree TEXT DEFAULT 'B.Tech',
        branch_full TEXT,
        dob TEXT,
        gender TEXT,
        regulation TEXT DEFAULT '2021',
        arrears TEXT DEFAULT '[]',
        active INTEGER DEFAULT 1
    )
    ''')
    
    # Seating allocations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seating_allocations (
        allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER,
        exam_date TEXT NOT NULL,
        session TEXT NOT NULL,
        hall_id INTEGER NOT NULL,
        hall_name TEXT NOT NULL,
        student_id INTEGER NOT NULL,
        reg_no TEXT NOT NULL,
        student_name TEXT NOT NULL,
        department TEXT NOT NULL,
        bench_number INTEGER NOT NULL,
        seat_no TEXT NOT NULL,
        position TEXT,
        exam_type TEXT NOT NULL,
        allocation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (hall_id) REFERENCES halls(hall_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    ''')
    
    # Hall assignments (teacher to hall mapping)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hall_assignments (
        assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_id INTEGER,
        hall_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cycle_id) REFERENCES exam_cycles(cycle_id),
        FOREIGN KEY (hall_id) REFERENCES halls(hall_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
    )
    ''')
    
    # Student subjects mapping (for hall tickets)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_subjects (
        mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        is_arrear INTEGER DEFAULT 0,
        registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        UNIQUE(student_id, subject_id)
    )
    ''')
    
    conn.commit()
    print("All tables created successfully")


def populate_subjects_data(conn):
    """Populate subjects data for all departments, years, and exam types"""
    cursor = conn.cursor()
    
    departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
    
    # Student counts per department
    dept_student_counts = {
        'CSE': 120,
        'ECE': 117,
        'MECH': 130,
        'CIVIL': 139,
        'EEE': 148
    }
    
    subjects_data = []
    
    # Year 1 - Semester 1 (ODD)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}101', f'{dept} Sub1', dept, 1, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}102', f'{dept} Sub2', dept, 1, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}103', f'{dept} Sub3', dept, 1, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}104', f'{dept} Sub4', dept, 1, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}105', f'{dept} Sub5', dept, 1, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}106', f'{dept} Sub6', dept, 1, 'ODD', 'Theory', 'BOTH', count),
        ])
    
    # Year 1 - Semester 2 (EVEN)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}201', f'{dept} Sub1', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}202', f'{dept} Sub2', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}203', f'{dept} Sub3', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}204', f'{dept} Sub4', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}205', f'{dept} Sub5', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}206', f'{dept} Sub6', dept, 1, 'EVEN', 'Theory', 'BOTH', count),
        ])
    
    # Year 2 - Semester 3 (ODD)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}301', f'{dept} Sub1', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}302', f'{dept} Sub2', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}303', f'{dept} Sub3', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}304', f'{dept} Sub4', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}305', f'{dept} Sub5', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}306', f'{dept} Sub6', dept, 2, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}307', f'{dept} Sub7', dept, 2, 'ODD', 'Theory', 'BOTH', count),
        ])
    
    # Year 2 - Semester 4 (EVEN)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}401', f'{dept} Sub1', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}402', f'{dept} Sub2', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}403', f'{dept} Sub3', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}404', f'{dept} Sub4', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}405', f'{dept} Sub5', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}406', f'{dept} Sub6', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}407', f'{dept} Sub7', dept, 2, 'EVEN', 'Theory', 'BOTH', count),
        ])
    
    # Year 3 - Semester 5 (ODD)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}501', f'{dept} Sub1', dept, 3, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}502', f'{dept} Sub2', dept, 3, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}503', f'{dept} Sub3', dept, 3, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}504', f'{dept} Sub4', dept, 3, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}505', f'{dept} Sub5', dept, 3, 'ODD', 'Theory', 'BOTH', count),
        ])
    
    # Year 3 - Semester 6 (EVEN)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}601', f'{dept} Sub1', dept, 3, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}602', f'{dept} Sub2', dept, 3, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}603', f'{dept} Sub3', dept, 3, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}604', f'{dept} Sub4', dept, 3, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}605', f'{dept} Sub5', dept, 3, 'EVEN', 'Theory', 'BOTH', count),
        ])
    
    # Year 4 - Semester 7 (ODD)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}701', f'{dept} Sub1', dept, 4, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}702', f'{dept} Sub2', dept, 4, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}703', f'{dept} Sub3', dept, 4, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}704', f'{dept} Sub4', dept, 4, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}705', f'{dept} Sub5', dept, 4, 'ODD', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}706', f'{dept} Sub6', dept, 4, 'ODD', 'Theory', 'BOTH', count),
        ])
    
    # Year 4 - Semester 8 (EVEN)
    for dept in departments:
        count = dept_student_counts[dept]
        subjects_data.extend([
            (f'21{dept[:2]}801', f'{dept} Sub1', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}802', f'{dept} Sub2', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}803', f'{dept} Sub3', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}804', f'{dept} Sub4', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}805', f'{dept} Sub5', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
            (f'21{dept[:2]}806', f'{dept} Sub6', dept, 4, 'EVEN', 'Theory', 'BOTH', count),
        ])
    
    # Insert subjects
    cursor.executemany('''
        INSERT OR IGNORE INTO subjects 
        (subject_code, subject_name, department, year, semester_type, subject_type, exam_type, student_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', subjects_data)
    
    conn.commit()
    print(f"Inserted {len(subjects_data)} subjects")


def populate_halls_data(conn):
    """Populate halls data (from halls.csv equivalent)"""
    cursor = conn.cursor()
    
    halls_data = [
        ('Hall 1', 30, 5),
        ('Hall 2', 30, 6),
        ('Hall 3', 32, 4),
        ('Hall 4', 32, 6),
        ('Hall 5', 32, 5),
        ('Hall 6', 28, 4),
        ('Hall 7', 28, 5),
        ('Hall 8', 35, 5),
        ('Hall 9', 35, 6),
        ('Hall 10', 30, 4),
        ('Hall 11', 30, 6),
        ('Hall 12', 32, 5),
        ('Hall 13', 32, 4),
        ('Hall 14', 28, 6),
        ('Hall 15', 28, 4),
        ('Hall 16', 35, 5),
        ('Hall 17', 35, 4),
        ('Hall 18', 30, 5),
        ('Hall 19', 30, 6),
        ('Hall 20', 32, 4),
        ('Hall 21', 28, 5),
        ('Hall 22', 28, 6),
        ('Hall 23', 35, 4),
        ('Hall 24', 35, 5),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO halls (hall_name, capacity, columns)
        VALUES (?, ?, ?)
    ''', halls_data)
    
    conn.commit()
    print(f"Inserted {len(halls_data)} halls")


def populate_teachers_data(conn):
    """Populate teachers/invigilators data (from teachers.csv equivalent)"""
    cursor = conn.cursor()
    
    teachers_data = [
        ('Dr. Rajesh Kumar', 'CSE', '9876543210'),
        ('Prof. Sanjay Reddy', 'ECE', '9876543211'),
        ('Dr. Venkat Rao', 'MECH', '9876543212'),
        ('Prof. Lakshmi Devi', 'CIVIL', '9876543213'),
        ('Dr. Prasad Naik', 'EEE', '9876543214'),
        ('Kumar', 'CSE', '9876543215'),
        ('Raghava', 'ECE', '9876543216'),
        ('Uthandam', 'MECH', '9876543217'),
        ('Saran', 'CIVIL', '9876543218'),
        ('Balaji', 'EEE', '9876543219'),
        ('Selvendran', 'CSE', '9876543220'),
        ('Vishal', 'ECE', '9876543221'),
        ('Vishnu Kumar', 'MECH', '9876543222'),
        ('Ragul', 'CIVIL', '9876543223'),
        ('Vasu', 'EEE', '9876543224'),
        ('Rithik', 'CSE', '9876543225'),
        ('Yogesh', 'ECE', '9876543226'),
        ('Dr. Suresh Babu', 'MECH', '9876543227'),
        ('Prof. Anusha Reddy', 'CIVIL', '9876543228'),
        ('Dr. Mahesh Kumar', 'EEE', '9876543229'),
        ('Prof. Divya Krishna', 'CSE', '9876543230'),
        ('Dr. Arun Kumar', 'ECE', '9876543231'),
        ('Prof. Swathi Rani', 'MECH', '9876543232'),
        ('Dr. Kiran Kumar', 'CIVIL', '9876543233'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO teachers (teacher_name, department, contact)
        VALUES (?, ?, ?)
    ''', teachers_data)
    
    conn.commit()
    print(f"Inserted {len(teachers_data)} teachers")


def populate_students_data(conn):
    """Populate students data for all years and departments"""
    cursor = conn.cursor()
    
    departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
    
    # Two-digit numeric department codes for register number
    dept_codes = {
        'CSE': '05',
        'ECE': '02',
        'MECH': '03',
        'CIVIL': '01',
        'EEE': '04'
    }
    
    branch_full_names = {
        'CSE': 'COMPUTER SCIENCE AND ENGINEERING',
        'ECE': 'ELECTRONICS AND COMMUNICATION ENGINEERING',
        'MECH': 'MECHANICAL ENGINEERING',
        'CIVIL': 'CIVIL ENGINEERING',
        'EEE': 'ELECTRICAL AND ELECTRONICS ENGINEERING'
    }
    
    students_data = []
    
    # Base joining year (current year - year + 1)
    current_year = 2025
    
    # Generate students for each year (1-4) and each department
    for year in range(1, 5):
        # Calculate joining year (e.g., Year 1 joined in 2025, Year 2 joined in 2024, etc.)
        joining_year = current_year - (year - 1)
        joining_year_2digit = joining_year % 100  # Get last 2 digits (2025 -> 25)
        
        for dept in departments:
            # Varying student counts per department
            student_counts = {'CSE': 120, 'ECE': 117, 'MECH': 130, 'CIVIL': 139, 'EEE': 148}
            count = student_counts.get(dept, 120)
            
            dept_code = dept_codes[dept]
            
            for i in range(1, count + 1):
                # New format: {YY}MLID{DD}{NNN}
                # Example: 25MLIDCS001, 24MLIDEC045
                reg_no = f"{joining_year_2digit}MLID{dept_code}{i:03d}"
                name = f"{dept} Student {i}"
                semester = (year * 2) if year < 4 else 8  # Year 1 -> Sem 2, Year 2 -> Sem 4, etc.
                dob = f"{i%28+1:02d}.{i%12+1:02d}.{2003+year}"
                gender = 'MALE' if i % 2 == 0 else 'FEMALE'
                
                students_data.append((
                    reg_no,
                    name,
                    dept,
                    year,
                    semester,
                    'B.Tech',
                    branch_full_names[dept],
                    dob,
                    gender,
                    '2021'
                ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO students 
        (reg_no, name, department, year, semester, degree, branch_full, dob, gender, regulation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', students_data)
    
    conn.commit()
    print(f"Inserted {len(students_data)} students across all years and departments")


def link_students_to_subjects(conn):
    """Link students to their respective subjects based on department and year, with some arrears"""
    cursor = conn.cursor()
    
    # Get all students
    cursor.execute('SELECT student_id, department, year, semester, reg_no FROM students')
    students = cursor.fetchall()
    
    # Get all subjects
    cursor.execute('SELECT subject_id, department, year, subject_code FROM subjects')
    subjects = cursor.fetchall()
    
    mappings = []
    arrear_count = 0
    
    for student in students:
        student_id, student_dept, student_year, student_sem, reg_no = student
        
        # Find matching subjects for this student's current year
        for subject in subjects:
            subject_id, subject_dept, subject_year, subject_code = subject
            
            # Match subjects from same department and year
            if student_dept == subject_dept and student_year == subject_year:
                mappings.append((student_id, subject_id, 0))  # 0 = not arrear
        
        # Add arrears for some students (approx 15% of students in years 2-4)
        if student_year >= 2:
            # Use student_id modulo to consistently select some students for arrears
            if student_id % 7 == 0:  # ~14% of students
                # Add 1-3 arrear subjects from previous year
                previous_year = student_year - 1
                arrear_subjects = [s for s in subjects if s[1] == student_dept and s[2] == previous_year]
                
                # Randomly select 1-3 subjects as arrears
                import random
                random.seed(student_id)  # Consistent randomness per student
                num_arrears = random.randint(1, min(3, len(arrear_subjects)))
                selected_arrears = random.sample(arrear_subjects, num_arrears)
                
                for subject in selected_arrears:
                    subject_id = subject[0]
                    mappings.append((student_id, subject_id, 1))  # 1 = arrear
                    arrear_count += 1
    
    cursor.executemany('''
        INSERT OR IGNORE INTO student_subjects (student_id, subject_id, is_arrear)
        VALUES (?, ?, ?)
    ''', mappings)
    
    conn.commit()
    print(f"Linked {len(mappings)} student-subject mappings (including {arrear_count} arrear subjects)")
    
    # Update students.arrears JSON array with their arrear subject codes
    import json
    cursor.execute('SELECT student_id FROM students')
    all_students = cursor.fetchall()
    
    for (student_id,) in all_students:
        # Get arrear subject codes for this student
        cursor.execute('''
            SELECT sub.subject_code
            FROM student_subjects ss
            JOIN subjects sub ON ss.subject_id = sub.subject_id
            WHERE ss.student_id = ? AND ss.is_arrear = 1
        ''', (student_id,))
        
        arrear_codes = [row[0] for row in cursor.fetchall()]
        arrear_json = json.dumps(arrear_codes)
        
        # Update student's arrears field
        cursor.execute('''
            UPDATE students
            SET arrears = ?
            WHERE student_id = ?
        ''', (arrear_json, student_id))
    
    conn.commit()
    print(f"Updated arrears JSON array for all students")


def display_database_summary(conn):
    """Display summary of database contents"""
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)
    
    # Count subjects
    cursor.execute('SELECT COUNT(*) FROM subjects')
    subject_count = cursor.fetchone()[0]
    print(f"Subjects: {subject_count}")
    
    # Count halls
    cursor.execute('SELECT COUNT(*) FROM halls')
    hall_count = cursor.fetchone()[0]
    print(f"Halls: {hall_count}")
    
    # Count teachers
    cursor.execute('SELECT COUNT(*) FROM teachers')
    teacher_count = cursor.fetchone()[0]
    print(f"Teachers: {teacher_count}")
    
    # Count students by year
    for year in range(1, 5):
        cursor.execute('SELECT COUNT(*) FROM students WHERE year = ?', (year,))
        count = cursor.fetchone()[0]
        print(f"Year {year} Students: {count}")
    
    # Count total students
    cursor.execute('SELECT COUNT(*) FROM students')
    total_students = cursor.fetchone()[0]
    print(f"Total Students: {total_students}")
    
    # Count student-subject mappings
    cursor.execute('SELECT COUNT(*) FROM student_subjects')
    mapping_count = cursor.fetchone()[0]
    print(f"Student-Subject Mappings: {mapping_count}")
    
    print("=" * 60)


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("INTEGRATED DATABASE SETUP")
    print("Database: exam_scheduling.db")
    print("=" * 60 + "\n")
    
    # Check if database exists
    if os.path.exists(DB_PATH):
        response = input("Database already exists. Recreate? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Setup cancelled.")
            return
        os.remove(DB_PATH)
        print("Removed existing database")
    
    # Create connection
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to database: {DB_PATH}")
    
    try:
        # Create all tables
        print("\n[1/6] Creating tables...")
        create_tables(conn)
        
        # Populate subjects
        print("\n[2/6] Populating subjects data...")
        populate_subjects_data(conn)
        
        # Populate halls
        print("\n[3/6] Populating halls data...")
        populate_halls_data(conn)
        
        # Populate teachers
        print("\n[4/6] Populating teachers data...")
        populate_teachers_data(conn)
        
        # Populate students
        print("\n[5/6] Populating students data...")
        populate_students_data(conn)
        
        # Link students to subjects
        print("\n[6/6] Linking students to subjects...")
        link_students_to_subjects(conn)
        
        # Display summary
        display_database_summary(conn)
        
        print("\nDatabase setup completed successfully!")
        print(f"\nDatabase location: {os.path.abspath(DB_PATH)}")
        print("\nYou can now run:")
        print("  1. Exam Scheduling Algorithm")
        print("  2. Seating Allocation System")
        print("  3. Hall Ticket Generation")
        
    except Exception as e:
        print(f"\nError during setup: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
