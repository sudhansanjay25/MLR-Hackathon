import random
from datetime import datetime, timedelta
from db import db, students_col, subjects_col, departments_col, users_col

# Constants
DEPARTMENTS = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL']
YEARS = [1, 2, 3, 4]
SEMESTERS = {
    1: [1, 2],
    2: [3, 4],
    3: [5, 6],
    4: [7, 8]
}

def clear_db():
    print("Clearing details...")
    students_col.delete_many({})
    subjects_col.delete_many({})
    departments_col.delete_many({})
    users_col.delete_many({})
    print("Database cleared.")

def seed_departments():
    print("Seeding departments...")
    for dept in DEPARTMENTS:
        departments_col.insert_one({'name': dept})

def seed_subjects():
    print("Seeding subjects...")
    subjects = []
    
    # Common subjects format: "SUB" + Year + Sem + Dept + Num
    
    for dept in DEPARTMENTS:
        for year in YEARS:
            for sem in SEMESTERS[year]:
                # 5-7 subjects per sem
                num_subjects = random.randint(5, 7)
                for i in range(1, num_subjects + 1):
                    # Mix of Major (Core) and Non-Major
                    is_major = True
                    if i > 4: # Last few are labs or electives or non-major
                         if random.random() > 0.7:
                             is_major = False
                    
                    subject_type = 'CORE' if is_major else 'NONMAJOR'
                    if i == num_subjects: # Make last one a Lab
                         subject_type = 'LAB'

                    subject = {
                        'code': f"{dept}{year}{sem}0{i}",
                        'name': f"{dept} Subject {sem}-{i}",
                        'department': dept,
                        'year': year,
                        'semester': sem,
                        'type': subject_type, # HEAVY, NORMAL, NONMAJOR, LAB
                        'credits': 3 if is_major else 2
                    }
                    subjects.append(subject)
    
    subjects_col.insert_many(subjects)
    print(f"Inserted {len(subjects)} subjects.")

def seed_students():
    print("Seeding students...")
    students = []
    
    # 60 students per class (Dept-Year)
    STUDENTS_PER_CLASS = 60
    
    current_year = 2024
    
    for dept in DEPARTMENTS:
        for year in YEARS:
            # Batch year calculation
            # Year 1 (joined 2024) -> Batch 2024-2028
            # Year 4 (joined 2021) -> Batch 2021-2025
            join_year = current_year - year + 1
            
            # Sem calculation (assume current sem is ODD)
            current_sem = (year * 2) - 1
            
            for i in range(1, STUDENTS_PER_CLASS + 1):
                # Reg No Format: 7140 + Year(2 digits) + DeptCode(2 dig) + Num(3 dig)
                # Mock Dept Code map
                dept_code_map = {'CSE': '05', 'ECE': '04', 'EEE': '03', 'MECH': '02', 'CIVIL': '01'}
                
                reg_no = f"7140{str(join_year)[-2:]}{dept_code_map[dept]}{i:03d}"
                
                student = {
                    'register_number': reg_no,
                    'name': f"Student {dept} {i}",
                    'department': dept,
                    'year': year,
                    'semester': current_sem,
                    'email': f"{reg_no}@mlrit.ac.in",
                    'password': 'student123', # Hash this in real app
                    'gender': "M" if random.random() > 0.5 else "F",
                    'regulation': 'R22'
                }
                students.append(student)
                
                # Create User entry for login
                users_col.insert_one({
                    'email': student['email'],
                    'password': student['password'],
                    'role': 'student',
                    'name': student['name'],
                    'id': reg_no,
                    'related_id': students_col.find_one({'register_number': reg_no}) # Logic circular, just storing ID is fine
                })

    students_col.insert_many(students)
    print(f"Inserted {len(students)} students.")

def seed_users():
    # COE and Faculty
    users = [
        {'email': 'coe@mlrit.ac.in', 'password': 'coe123', 'role': 'coe', 'name': 'Chief Superintendent', 'id': 'COE001'},
        {'email': 'faculty001@mlrit.ac.in', 'password': 'faculty123', 'role': 'faculty', 'name': 'Dr. A. Sharma', 'id': 'FAC001'}
    ]
    users_col.insert_many(users)
    print("Inserted admin users.")

if __name__ == "__main__":
    clear_db()
    seed_departments()
    seed_subjects()
    seed_students()
    seed_users()
    print("Database seeding completed.")
