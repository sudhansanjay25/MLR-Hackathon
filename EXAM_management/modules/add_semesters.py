"""
Update subjects to have proper semester field
Each year has 2 semesters:
- Subjects with codes ending in 01-06 -> Semester 1
- Subjects with codes ending in 01-06 in second half -> Semester 2
"""
from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['exam_management']

print("=" * 60)
print("ADDING SEMESTER FIELD TO SUBJECTS")
print("=" * 60)

for year in [1, 2, 3, 4]:
    subjects = list(db.subjects.find({'year': year}).sort('code', 1))
    
    print(f"\nYear {year}: {len(subjects)} subjects")
    
    # Group subjects by department
    by_dept = {}
    for s in subjects:
        dept_id = s.get('department')
        if dept_id:
            dept = db.departments.find_one({'_id': dept_id})
            if dept:
                dept_code = dept['code']
                if dept_code not in by_dept:
                    by_dept[dept_code] = []
                by_dept[dept_code].append(s)
    
    # Update semester for each department's subjects
    for dept_code, dept_subjects in by_dept.items():
        # Sort by code
        dept_subjects.sort(key=lambda x: x['code'])
        
        # First half -> Sem 1, Second half -> Sem 2
        mid_point = len(dept_subjects) // 2
        
        for i, subj in enumerate(dept_subjects):
            semester = 1 if i < mid_point else 2
            
            # Update in database
            db.subjects.update_one(
                {'_id': subj['_id']},
                {'$set': {'semester': semester}}
            )
        
        sem1_count = len([s for s in dept_subjects[:mid_point]])
        sem2_count = len([s for s in dept_subjects[mid_point:]])
        print(f"  {dept_code}: Sem 1 = {sem1_count} subjects, Sem 2 = {sem2_count} subjects")

# Verify
print("\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)

for year in [1, 2, 3, 4]:
    sem1_count = db.subjects.count_documents({'year': year, 'semester': 1})
    sem2_count = db.subjects.count_documents({'year': year, 'semester': 2})
    print(f"Year {year}: Sem 1 = {sem1_count} subjects, Sem 2 = {sem2_count} subjects")

print("\n✅ All subjects updated with semester field!")

client.close()
