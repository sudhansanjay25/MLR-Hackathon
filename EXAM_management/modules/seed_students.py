from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['exam_management']

# Get departments
departments = list(db.departments.find({}))
if not departments:
    print("No departments found! Please create departments first.")
    exit(1)

print(f"Found {len(departments)} departments")

# Clear existing students (except test ones)
db.students.delete_many({'registerNumber': {'$regex': '^714'}})
print("Cleared existing students")

# Student data
students = []
base_year = 2021
current_year = 4  # 4th years are seniors

# Distribute students across departments and years
students_per_dept_per_year = {
    1: 100,  # Year 1: 100 students per dept
    2: 100,  # Year 2: 100 students per dept
    3: 100,  # Year 3: 100 students per dept
    4: 100   # Year 4: 100 students per dept
}

# Generate students
student_id = 1
for dept in departments:
    dept_code = dept['code']
    dept_name = dept['name']
    
    print(f"\nGenerating students for {dept_name} ({dept_code})...")
    
    for year in range(1, 5):  # Years 1-4
        num_students = students_per_dept_per_year[year]
        
        for i in range(num_students):
            # Register number format: 714YYDDSSS
            # 714 = college code
            # YY = year of admission (21, 22, 23, 24)
            # DD = dept code (01=CSE, 02=ECE, etc)
            # SSS = serial number
            
            admission_year = 25 - year  # 2025-year gives admission year
            dept_num = str(departments.index(dept) + 1).zfill(2)
            serial = str(i + 1).zfill(3)
            
            reg_no = f"714{admission_year}{dept_num}{serial}"
            
            student = {
                'registerNumber': reg_no,
                'name': f"{dept_code} Student {serial}",
                'email': f"{reg_no}@mlrit.ac.in",
                'department': dept['_id'],
                'yearOfStudy': year,
                'year': year,
                'semester': year * 2,  # Semester = year * 2
                'degree': 'B.Tech',
                'branch': dept_name,
                'dateOfBirth': datetime(2005 - year, 1, 1),
                'gender': 'Male' if i % 2 == 0 else 'Female',
                'regulation': 'R21',
                'isActive': True,
                'createdAt': datetime.now(),
                'updatedAt': datetime.now()
            }
            
            students.append(student)
            student_id += 1
        
        print(f"  Year {year}: {num_students} students")

# Insert students
if students:
    db.students.insert_many(students)
    print(f"\n✅ Successfully created {len(students)} students!")
    
    # Show summary
    print("\nSummary by Year:")
    for year in range(1, 5):
        count = len([s for s in students if s['year'] == year])
        print(f"  Year {year}: {count} students")
    
    print(f"\nSummary by Department:")
    for dept in departments:
        count = len([s for s in students if s['department'] == dept['_id']])
        print(f"  {dept['code']}: {count} students")
else:
    print("No students to insert")

client.close()
