import sqlite3

conn = sqlite3.connect('exam_scheduling.db')
cursor = conn.cursor()

print("="*80)
print("VERIFICATION: Who should appear for 3rd Year EVEN semester exam?")
print("="*80)

# Check subjects scheduled for 23.12.2025 FN
cursor.execute('''
    SELECT sub.subject_code, sub.subject_name, sub.year, sub.semester_type
    FROM schedules sch
    JOIN subjects sub ON sch.subject_id = sub.subject_id
    WHERE sch.exam_date = '23.12.2025' AND sch.session = 'FN'
''')

subjects = cursor.fetchall()
print("\nSubjects scheduled for 23.12.2025 FN:")
for code, name, year, sem_type in subjects:
    print(f"  {code} - {name} (Year {year}, {sem_type} semester)")

subject_codes = [s[0] for s in subjects]

# Check current students (Year 3, currently in ODD semester)
print("\n" + "="*80)
print("Current Third Year Students (should NOT appear for EVEN semester yet):")
print("="*80)

cursor.execute('''
    SELECT student_id, reg_no, name, department, year, semester
    FROM students
    WHERE year = 3 AND active = 1
    LIMIT 5
''')

for sid, reg, name, dept, yr, sem in cursor.fetchall():
    print(f"  {reg} - {name} ({dept}) | Current: Year {yr}, Semester {sem}")
    # Calculate expected semester: Year 3 should be in Semester 5 or 6
    # If currently December 2025, Year 3 students should be in Semester 5 (ODD)
    expected_sem = 5 if sem % 2 == 1 else 6
    print(f"    → Currently in: Semester {sem} ({'ODD' if sem % 2 == 1 else 'EVEN'})")

# Check passed-out students with arrears
print("\n" + "="*80)
print("Passed-out Students with arrears in scheduled subjects (SHOULD appear):")
print("="*80)

cursor.execute(f'''
    SELECT s.student_id, s.reg_no, s.name, s.department, s.year, s.arrears
    FROM students s
    WHERE s.year = 5 AND s.active = 1 AND s.arrears IS NOT NULL
''')

import json
count = 0
for sid, reg, name, dept, yr, arrears_json in cursor.fetchall():
    if arrears_json:
        arrears_list = json.loads(arrears_json)
        # Check if any scheduled subject is in arrears
        matching_arrears = [a for a in arrears_list if a in subject_codes]
        if matching_arrears:
            count += 1
            if count <= 5:
                print(f"  {reg} - {name} ({dept}) | Arrears: {', '.join(matching_arrears)}")

print(f"\nTotal passed-out students with arrears in these subjects: {count}")

# The problem query
print("\n" + "="*80)
print("PROBLEM: Current query selects these as 'Regular' students:")
print("="*80)

placeholders = ','.join(['?' for _ in subject_codes])
cursor.execute(f'''
    SELECT DISTINCT s.student_id, s.reg_no, s.name, s.department, s.year
    FROM students s
    JOIN student_subjects ss ON s.student_id = ss.student_id
    JOIN subjects sub ON ss.subject_id = sub.subject_id
    WHERE sub.subject_code IN ({placeholders})
        AND s.active = 1
        AND ss.is_arrear = 0
        AND s.year = 3
        AND sub.semester_type = 'EVEN'
    ORDER BY s.department, s.reg_no
    LIMIT 10
''', subject_codes)

regular = cursor.fetchall()
print(f"\nFound {len(regular)} 'regular' students")
if regular:
    print("Sample:")
    for sid, reg, name, dept, yr in regular[:5]:
        print(f"  {reg} - {name} ({dept}, Year {yr})")

print("\n" + "="*80)
print("SOLUTION: Students should only appear if:")
print("="*80)
print("  1. They are enrolled in the subject (student_subjects table)")
print("  2. They are CURRENTLY in that semester (student.semester matches subject)")
print("  3. OR they have arrears in that subject")

conn.close()
