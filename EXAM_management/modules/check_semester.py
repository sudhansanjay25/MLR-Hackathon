from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['exam_management']

print("=" * 60)
print("CHECKING SUBJECTS SEMESTER STRUCTURE")
print("=" * 60)

# Check if subjects have semester field
sample_subjects = list(db.subjects.find({'year': 2}).limit(20))
print(f"\nTotal Year 2 subjects: {db.subjects.count_documents({'year': 2})}")

has_semester = any('semester' in s for s in sample_subjects)
print(f"\nSubjects have 'semester' field: {has_semester}")

if has_semester:
    print("\nSemester distribution:")
    for year in [1, 2, 3, 4]:
        for sem in [1, 2]:
            count = db.subjects.count_documents({'year': year, 'semester': sem})
            print(f"  Year {year}, Sem {sem}: {count} subjects")
else:
    print("\n⚠️  Subjects DON'T have semester field!")
    print("\nSample subject structure:")
    if sample_subjects:
        print(f"  Fields: {list(sample_subjects[0].keys())}")
        for s in sample_subjects[:5]:
            print(f"  {s['code']}: {s['name']}")
    
    print("\n📝 Need to add semester field to subjects!")

client.close()
