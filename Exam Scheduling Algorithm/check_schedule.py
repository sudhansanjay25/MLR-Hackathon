import sqlite3

conn = sqlite3.connect('exam_scheduling.db')
cursor = conn.cursor()

# Check what's scheduled for 23.12.2025 FN
cursor.execute('''
    SELECT sub.subject_code, sub.subject_name, sub.year, sub.semester_type
    FROM schedules sch
    JOIN subjects sub ON sch.subject_id = sub.subject_id
    WHERE sch.exam_date = '23.12.2025' AND sch.session = 'FN'
    ORDER BY sub.department, sub.subject_code
''')

print("="*80)
print("Subjects scheduled for 23.12.2025 FN:")
print("="*80)

odd_count = 0
even_count = 0

for code, name, year, sem_type in cursor.fetchall():
    print(f"{code:15} - {name:30} (Year {year}, {sem_type})")
    if sem_type == 'ODD':
        odd_count += 1
    else:
        even_count += 1

print(f"\n{odd_count} ODD semester subjects, {even_count} EVEN semester subjects")
print(f"Total: {odd_count + even_count} subjects")

conn.close()
