"""
Add passed-out students (2021 batch) with arrears in 3rd and 4th year subjects
These students have completed their B.Tech but have pending arrears
"""

import sqlite3
import json

def add_passedout_students_with_arrears():
    """Add 2021 batch students (passed out) with arrears from 3rd and 4th year"""
    
    conn = sqlite3.connect('exam_scheduling.db')
    cursor = conn.cursor()
    
    departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
    dept_codes = {
        'CSE': '05',
        'ECE': '02',
        'MECH': '03',
        'CIVIL': '01',
        'EEE': '04'
    }
    
    # Subject code prefixes (different from register number codes)
    dept_subject_codes = {
        'CSE': 'CS',
        'ECE': 'EC',
        'MECH': 'ME',
        'CIVIL': 'CI',
        'EEE': 'EE'
    }
    
    branch_full_names = {
        'CSE': 'COMPUTER SCIENCE AND ENGINEERING',
        'ECE': 'ELECTRONICS AND COMMUNICATION ENGINEERING',
        'MECH': 'MECHANICAL ENGINEERING',
        'CIVIL': 'CIVIL ENGINEERING',
        'EEE': 'ELECTRICAL AND ELECTRONICS ENGINEERING'
    }
    
    # Get 3rd and 4th year subjects for arrears
    cursor.execute('''
        SELECT subject_code, department, year, semester_type 
        FROM subjects 
        WHERE year IN (3, 4)
        ORDER BY department, year, semester_type
    ''')
    all_subjects = cursor.fetchall()
    
    # Group subjects by department
    dept_subjects = {dept: [] for dept in departments}
    for subject_code, dept, year, sem_type in all_subjects:
        dept_subjects[dept].append(subject_code)
    
    students_data = []
    
    # Add 10 passed-out students per department (total 50 students)
    for dept in departments:
        dept_code = dept_codes[dept]
        subject_code_prefix = dept_subject_codes[dept]
        
        for i in range(901, 911):  # Student numbers 901-910 (passed out students)
            # Register number format: 21MLID{DD}{NNN}
            # 21 = joined in 2021, passed out in 2025
            reg_no = f"21MLID{dept_code}{i:03d}"
            name = f"{dept} Passedout Student {i-900}"
            
            # These students have completed B.Tech (year=5 means passed out)
            year = 5
            semester = 8  # Completed all 8 semesters
            dob = f"{i%28+1:02d}.{i%12+1:02d}.2003"
            gender = 'MALE' if i % 2 == 0 else 'FEMALE'
            
            # Assign arrears from 3rd and 4th year subjects of their department
            arrears_list = []
            
            # Each student gets 2-4 arrear subjects
            # Mix of 3rd year and 4th year subjects
            
            if i % 2 == 0:
                # Even numbered students: 3rd year arrears (ODD + EVEN)
                arrears_list = [
                    f"21{subject_code_prefix}501",  # 3rd year ODD subject 1
                    f"21{subject_code_prefix}601",  # 3rd year EVEN subject 1
                ]
            else:
                # Odd numbered students: 4th year arrears (ODD + EVEN)
                arrears_list = [
                    f"21{subject_code_prefix}701",  # 4th year ODD subject 1
                    f"21{subject_code_prefix}801",  # 4th year EVEN subject 1
                ]
            
            # Some students have both 3rd and 4th year arrears
            if i % 3 == 0:
                arrears_list.append(f"21{subject_code_prefix}502")  # 3rd year ODD subject 2
            if i % 5 == 0:
                arrears_list.append(f"21{subject_code_prefix}702")  # 4th year ODD subject 2
            
            arrears_json = json.dumps(arrears_list)
            
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
                '2021',
                arrears_json,
                1  # active = 1
            ))
    
    # Insert passed-out students
    cursor.executemany('''
        INSERT OR REPLACE INTO students 
        (reg_no, name, department, year, semester, degree, branch_full, dob, gender, regulation, arrears, active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', students_data)
    
    conn.commit()
    
    print(f"\n{'='*60}")
    print("PASSED-OUT STUDENTS ADDED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"Total students added: {len(students_data)}")
    print(f"\nBreakdown by department:")
    for dept in departments:
        dept_students = [s for s in students_data if s[2] == dept]
        print(f"  {dept}: {len(dept_students)} students")
    
    print(f"\n{'='*60}")
    print("Sample Students with Arrears:")
    print(f"{'='*60}")
    
    # Display first 3 students as samples
    for i, student in enumerate(students_data[:3]):
        reg_no, name, dept, year, sem, degree, branch, dob, gender, reg, arrears, active = student
        arrears_list = json.loads(arrears)
        print(f"\n{i+1}. {reg_no} - {name}")
        print(f"   Department: {dept}")
        print(f"   Year: {year} (Passed Out)")
        print(f"   Arrears: {', '.join(arrears_list)}")
    
    # Link passed-out students to their arrear subjects in student_subjects table
    print(f"\n{'='*60}")
    print("Linking students to arrear subjects...")
    print(f"{'='*60}")
    
    for student in students_data:
        reg_no = student[0]
        arrears_json = student[10]
        arrears_list = json.loads(arrears_json)
        
        # Get student_id
        cursor.execute('SELECT student_id FROM students WHERE reg_no = ?', (reg_no,))
        result = cursor.fetchone()
        if not result:
            continue
        student_id = result[0]
        
        # Link to arrear subjects
        for subject_code in arrears_list:
            cursor.execute('SELECT subject_id FROM subjects WHERE subject_code = ?', (subject_code,))
            subject_result = cursor.fetchone()
            if subject_result:
                subject_id = subject_result[0]
                cursor.execute('''
                    INSERT OR IGNORE INTO student_subjects (student_id, subject_id, is_arrear)
                    VALUES (?, ?, 1)
                ''', (student_id, subject_id))
    
    conn.commit()
    print("✓ Arrear subjects linked successfully")
    
    # Verify the data
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print(f"{'='*60}")
    
    cursor.execute('''
        SELECT COUNT(*) FROM students WHERE year = 5 AND arrears != '[]'
    ''')
    count = cursor.fetchone()[0]
    print(f"Total passed-out students with arrears: {count}")
    
    cursor.execute('''
        SELECT s.reg_no, s.name, s.department, COUNT(ss.subject_id) as arrear_count
        FROM students s
        LEFT JOIN student_subjects ss ON s.student_id = ss.student_id AND ss.is_arrear = 1
        WHERE s.year = 5
        GROUP BY s.student_id
        LIMIT 5
    ''')
    
    print(f"\nSample verification (first 5 students):")
    for reg_no, name, dept, arrear_count in cursor.fetchall():
        print(f"  {reg_no} ({dept}): {arrear_count} arrear subjects")
    
    conn.close()
    print(f"\n{'='*60}")
    print("DONE!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    add_passedout_students_with_arrears()
