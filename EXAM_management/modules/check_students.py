from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['exam_management']

students = list(db.students.find({}))
print(f'Total students: {len(students)}\n')

for i, s in enumerate(students, 1):
    reg = s.get('registerNumber', s.get('registerNo', 'NO_REG'))
    name = s.get('name', s.get('studentName', 'NO_NAME'))
    year = s.get('yearOfStudy', s.get('year', '?'))
    active = s.get('isActive', 'not set')
    print(f'{i}. {reg}: {name} - Year {year} - Active: {active}')

client.close()
