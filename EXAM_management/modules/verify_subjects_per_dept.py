from pymongo import MongoClient

client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['exam_management']

print("=" * 60)
print("SUBJECT DISTRIBUTION PER DEPARTMENT")
print("=" * 60)

departments = list(db.departments.find())

for year in [1, 2, 3, 4]:
    print(f"\n{'='*60}")
    print(f"YEAR {year}")
    print(f"{'='*60}")
    
    for dept in departments:
        dept_code = dept['code']
        
        sem1_count = db.subjects.count_documents({
            'year': year,
            'semester': 1,
            'department': dept['_id']
        })
        
        sem2_count = db.subjects.count_documents({
            'year': year,
            'semester': 2,
            'department': dept['_id']
        })
        
        if sem1_count > 0 or sem2_count > 0:
            print(f"{dept_code:8} -> Sem 1: {sem1_count} subjects, Sem 2: {sem2_count} subjects")
    
    # Total for year
    total_sem1 = db.subjects.count_documents({'year': year, 'semester': 1})
    total_sem2 = db.subjects.count_documents({'year': year, 'semester': 2})
    print(f"\n{'Total':<8} -> Sem 1: {total_sem1} subjects, Sem 2: {total_sem2} subjects")

client.close()
