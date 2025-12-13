from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['exam_management']

# Check subjects structure
print("=" * 60)
print("CHECKING SUBJECTS STRUCTURE")
print("=" * 60)

subjects = list(db.subjects.find({'year': 2}, {'code': 1, 'name': 1, 'department': 1, 'year': 1}).sort('code', 1).limit(15))
print(f"\nFound {db.subjects.count_documents({'year': 2})} subjects for Year 2")
print("\nSample subjects:")
for s in subjects:
    dept_id = s.get('department', 'N/A')
    if dept_id != 'N/A':
        dept = db.departments.find_one({'_id': dept_id})
        dept_name = dept['code'] if dept else 'Unknown'
    else:
        dept_name = 'N/A'
    print(f"  {s['code']}: {s['name'][:40]:<40} - Dept: {dept_name}")

# Check if subjects are department-specific
print("\n" + "=" * 60)
print("DEPARTMENT DISTRIBUTION")
print("=" * 60)
for year in [1, 2, 3, 4]:
    subjects = list(db.subjects.find({'year': year}))
    print(f"\nYear {year}: {len(subjects)} subjects")
    
    dept_counts = {}
    for s in subjects:
        dept_id = s.get('department')
        if dept_id:
            dept = db.departments.find_one({'_id': dept_id})
            dept_code = dept['code'] if dept else 'Unknown'
            dept_counts[dept_code] = dept_counts.get(dept_code, 0) + 1
    
    for dept, count in sorted(dept_counts.items()):
        print(f"  {dept}: {count} subjects")

client.close()
