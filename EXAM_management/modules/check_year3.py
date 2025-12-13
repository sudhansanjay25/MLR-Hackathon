from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['exam_management']

# Check Year 3 subjects structure
subjects = list(db.subjects.find({'year': 3}).limit(3))

print("Year 3 subjects structure:\n")
for s in subjects:
    print(f"Code: {s.get('code')}")
    print(f"Name: {s.get('name')}")
    print(f"Year: {s.get('year')}")
    print(f"Semester: {s.get('semester', 'NOT SET')}")
    print(f"Department: {s.get('department')}")
    print(f"IsActive: {s.get('isActive')}")
    print("-" * 50)
