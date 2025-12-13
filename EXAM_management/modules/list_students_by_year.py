from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['exam_management']

# Get all students
students = list(db.students.find({}))

print(f'Total students in database: {len(students)}\n')

# Count by year
year_counts = {}
for s in students:
    year = s.get('yearOfStudy', s.get('year', 'Unknown'))
    if year not in year_counts:
        year_counts[year] = {'total': 0, 'active': 0, 'inactive': 0}
    
    year_counts[year]['total'] += 1
    
    is_active = s.get('isActive')
    if is_active == True:
        year_counts[year]['active'] += 1
    elif is_active == False:
        year_counts[year]['inactive'] += 1
    else:
        year_counts[year]['inactive'] += 1  # Treat missing as inactive

print('Students by Year:')
print('-' * 60)
for year in sorted(year_counts.keys()):
    counts = year_counts[year]
    print(f'Year {year}: {counts["total"]} total, {counts["active"]} active, {counts["inactive"]} inactive')

print('\nDetailed List:')
print('-' * 60)
for year in sorted(year_counts.keys()):
    print(f'\nYear {year}:')
    year_students = [s for s in students if s.get('yearOfStudy', s.get('year')) == year]
    for i, s in enumerate(year_students, 1):
        reg = s.get('registerNumber', s.get('registerNo', 'NO_REG'))
        name = s.get('name', s.get('studentName', 'NO_NAME'))
        active = s.get('isActive', 'not set')
        print(f'  {i}. {reg}: {name} - Active: {active}')

client.close()
