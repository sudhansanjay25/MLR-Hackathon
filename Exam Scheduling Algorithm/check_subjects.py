import sqlite3

conn = sqlite3.connect('exam_scheduling.db')
cursor = conn.cursor()

# Check actual subject codes for year 3 and 4
cursor.execute('''
    SELECT subject_code, subject_name, department, year, semester_type 
    FROM subjects 
    WHERE year IN (3, 4) 
    ORDER BY department, year, semester_type
    LIMIT 20
''')

print("Sample Subject Codes (Year 3 & 4):")
print("="*80)
for code, name, dept, year, sem in cursor.fetchall():
    print(f"{code:15} - {name:30} ({dept}, Year {year}, {sem})")

conn.close()
