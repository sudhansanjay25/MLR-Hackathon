"""
Database Setup Script
Generates all mock data for the Exam Management System
"""
import random
from config import (
    get_db, DEPARTMENTS, YEAR_MAPPING, SEMESTER_MAPPING,
    STUDENTS_PER_DEPT_PER_YEAR, TOTAL_FACULTY, TOTAL_HALLS,
    MIN_BENCH_CAPACITY, MAX_BENCH_CAPACITY, MIN_COLUMNS, MAX_COLUMNS,
    DEFAULT_PASSWORD, SUBJECT_TYPES
)

# Sample names for generating mock data
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Ayaan", "Krishna",
    "Ishaan", "Sai", "Ananya", "Diya", "Pihu", "Prisha", "Anika", "Sara", "Myra",
    "Ira", "Saanvi", "Aanya", "Rohan", "Karthik", "Rahul", "Vikram", "Suresh",
    "Amit", "Priya", "Sneha", "Neha", "Pooja", "Ravi", "Sanjay", "Deepak",
    "Raj", "Nikhil", "Akash", "Shreya", "Kavya", "Meera", "Lakshmi"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Kumar", "Singh", "Reddy", "Nair", "Iyer",
    "Menon", "Pillai", "Rao", "Naidu", "Gupta", "Joshi", "Desai", "Shah",
    "Mehta", "Agarwal", "Chopra", "Kapoor", "Malhotra", "Saxena", "Bhat",
    "Hegde", "Shetty", "Kulkarni", "Patil", "Jain", "Bansal", "Mittal"
]

DEPARTMENT_NAMES = {
    101: "Computer Science",
    201: "Electronics",
    301: "Mechanical",
    401: "Civil",
    501: "Electrical"
}

# Subjects per semester (4-5 subjects each)
SUBJECTS_DATA = {
    # Year 1
    1: {  # Semester 1 (Odd)
        101: [
            {"code": "CS101", "name": "Programming Fundamentals", "type": "HEAVY"},
            {"code": "CS102", "name": "Digital Logic", "type": "HEAVY"},
            {"code": "MA101", "name": "Engineering Mathematics I", "type": "HEAVY"},
            {"code": "PH101", "name": "Engineering Physics", "type": "NONMAJOR"},
            {"code": "EN101", "name": "Technical English", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC101", "name": "Basic Electronics", "type": "HEAVY"},
            {"code": "EC102", "name": "Circuit Theory", "type": "HEAVY"},
            {"code": "MA101", "name": "Engineering Mathematics I", "type": "HEAVY"},
            {"code": "PH101", "name": "Engineering Physics", "type": "NONMAJOR"},
            {"code": "EN101", "name": "Technical English", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME101", "name": "Engineering Mechanics", "type": "HEAVY"},
            {"code": "ME102", "name": "Engineering Drawing", "type": "HEAVY"},
            {"code": "MA101", "name": "Engineering Mathematics I", "type": "HEAVY"},
            {"code": "PH101", "name": "Engineering Physics", "type": "NONMAJOR"},
            {"code": "EN101", "name": "Technical English", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE101", "name": "Engineering Surveying", "type": "HEAVY"},
            {"code": "CE102", "name": "Building Materials", "type": "HEAVY"},
            {"code": "MA101", "name": "Engineering Mathematics I", "type": "HEAVY"},
            {"code": "PH101", "name": "Engineering Physics", "type": "NONMAJOR"},
            {"code": "EN101", "name": "Technical English", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE101", "name": "Basic Electrical Engineering", "type": "HEAVY"},
            {"code": "EE102", "name": "Electrical Circuits", "type": "HEAVY"},
            {"code": "MA101", "name": "Engineering Mathematics I", "type": "HEAVY"},
            {"code": "PH101", "name": "Engineering Physics", "type": "NONMAJOR"},
            {"code": "EN101", "name": "Technical English", "type": "NONMAJOR"}
        ]
    },
    2: {  # Semester 2 (Even)
        101: [
            {"code": "CS201", "name": "Data Structures", "type": "HEAVY"},
            {"code": "CS202", "name": "Object Oriented Programming", "type": "HEAVY"},
            {"code": "MA102", "name": "Engineering Mathematics II", "type": "HEAVY"},
            {"code": "CH101", "name": "Engineering Chemistry", "type": "NONMAJOR"},
            {"code": "EN102", "name": "Communication Skills", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC201", "name": "Electronic Devices", "type": "HEAVY"},
            {"code": "EC202", "name": "Network Analysis", "type": "HEAVY"},
            {"code": "MA102", "name": "Engineering Mathematics II", "type": "HEAVY"},
            {"code": "CH101", "name": "Engineering Chemistry", "type": "NONMAJOR"},
            {"code": "EN102", "name": "Communication Skills", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME201", "name": "Thermodynamics", "type": "HEAVY"},
            {"code": "ME202", "name": "Manufacturing Processes", "type": "HEAVY"},
            {"code": "MA102", "name": "Engineering Mathematics II", "type": "HEAVY"},
            {"code": "CH101", "name": "Engineering Chemistry", "type": "NONMAJOR"},
            {"code": "EN102", "name": "Communication Skills", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE201", "name": "Strength of Materials", "type": "HEAVY"},
            {"code": "CE202", "name": "Fluid Mechanics", "type": "HEAVY"},
            {"code": "MA102", "name": "Engineering Mathematics II", "type": "HEAVY"},
            {"code": "CH101", "name": "Engineering Chemistry", "type": "NONMAJOR"},
            {"code": "EN102", "name": "Communication Skills", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE201", "name": "Electrical Machines I", "type": "HEAVY"},
            {"code": "EE202", "name": "Electromagnetic Theory", "type": "HEAVY"},
            {"code": "MA102", "name": "Engineering Mathematics II", "type": "HEAVY"},
            {"code": "CH101", "name": "Engineering Chemistry", "type": "NONMAJOR"},
            {"code": "EN102", "name": "Communication Skills", "type": "NONMAJOR"}
        ]
    },
    3: {  # Semester 3 (Odd)
        101: [
            {"code": "CS301", "name": "Database Management", "type": "HEAVY"},
            {"code": "CS302", "name": "Computer Networks", "type": "HEAVY"},
            {"code": "CS303", "name": "Operating Systems", "type": "HEAVY"},
            {"code": "MA201", "name": "Discrete Mathematics", "type": "NONMAJOR"},
            {"code": "HS201", "name": "Economics", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC301", "name": "Analog Circuits", "type": "HEAVY"},
            {"code": "EC302", "name": "Digital Signal Processing", "type": "HEAVY"},
            {"code": "EC303", "name": "Microprocessors", "type": "HEAVY"},
            {"code": "MA201", "name": "Discrete Mathematics", "type": "NONMAJOR"},
            {"code": "HS201", "name": "Economics", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME301", "name": "Fluid Mechanics", "type": "HEAVY"},
            {"code": "ME302", "name": "Kinematics of Machines", "type": "HEAVY"},
            {"code": "ME303", "name": "Material Science", "type": "HEAVY"},
            {"code": "MA201", "name": "Numerical Methods", "type": "NONMAJOR"},
            {"code": "HS201", "name": "Economics", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE301", "name": "Structural Analysis I", "type": "HEAVY"},
            {"code": "CE302", "name": "Geotechnical Engineering", "type": "HEAVY"},
            {"code": "CE303", "name": "Concrete Technology", "type": "HEAVY"},
            {"code": "MA201", "name": "Numerical Methods", "type": "NONMAJOR"},
            {"code": "HS201", "name": "Economics", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE301", "name": "Electrical Machines II", "type": "HEAVY"},
            {"code": "EE302", "name": "Power Systems I", "type": "HEAVY"},
            {"code": "EE303", "name": "Control Systems", "type": "HEAVY"},
            {"code": "MA201", "name": "Numerical Methods", "type": "NONMAJOR"},
            {"code": "HS201", "name": "Economics", "type": "NONMAJOR"}
        ]
    },
    4: {  # Semester 4 (Even)
        101: [
            {"code": "CS401", "name": "Algorithm Design", "type": "HEAVY"},
            {"code": "CS402", "name": "Software Engineering", "type": "HEAVY"},
            {"code": "CS403", "name": "Web Technologies", "type": "HEAVY"},
            {"code": "MA202", "name": "Probability & Statistics", "type": "NONMAJOR"},
            {"code": "HS202", "name": "Management Principles", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC401", "name": "Communication Systems", "type": "HEAVY"},
            {"code": "EC402", "name": "VLSI Design", "type": "HEAVY"},
            {"code": "EC403", "name": "Embedded Systems", "type": "HEAVY"},
            {"code": "MA202", "name": "Probability & Statistics", "type": "NONMAJOR"},
            {"code": "HS202", "name": "Management Principles", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME401", "name": "Heat Transfer", "type": "HEAVY"},
            {"code": "ME402", "name": "Dynamics of Machines", "type": "HEAVY"},
            {"code": "ME403", "name": "Machine Design I", "type": "HEAVY"},
            {"code": "MA202", "name": "Probability & Statistics", "type": "NONMAJOR"},
            {"code": "HS202", "name": "Management Principles", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE401", "name": "Structural Analysis II", "type": "HEAVY"},
            {"code": "CE402", "name": "Transportation Engineering", "type": "HEAVY"},
            {"code": "CE403", "name": "Environmental Engineering", "type": "HEAVY"},
            {"code": "MA202", "name": "Probability & Statistics", "type": "NONMAJOR"},
            {"code": "HS202", "name": "Management Principles", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE401", "name": "Power Systems II", "type": "HEAVY"},
            {"code": "EE402", "name": "Power Electronics", "type": "HEAVY"},
            {"code": "EE403", "name": "Instrumentation", "type": "HEAVY"},
            {"code": "MA202", "name": "Probability & Statistics", "type": "NONMAJOR"},
            {"code": "HS202", "name": "Management Principles", "type": "NONMAJOR"}
        ]
    },
    5: {  # Semester 5 (Odd)
        101: [
            {"code": "CS501", "name": "Machine Learning", "type": "HEAVY"},
            {"code": "CS502", "name": "Compiler Design", "type": "HEAVY"},
            {"code": "CS503", "name": "Computer Architecture", "type": "HEAVY"},
            {"code": "CS504", "name": "Information Security", "type": "NONMAJOR"},
            {"code": "OE501", "name": "Open Elective I", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC501", "name": "Wireless Communication", "type": "HEAVY"},
            {"code": "EC502", "name": "Antenna Theory", "type": "HEAVY"},
            {"code": "EC503", "name": "Optical Communication", "type": "HEAVY"},
            {"code": "EC504", "name": "IoT Systems", "type": "NONMAJOR"},
            {"code": "OE501", "name": "Open Elective I", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME501", "name": "IC Engines", "type": "HEAVY"},
            {"code": "ME502", "name": "Machine Design II", "type": "HEAVY"},
            {"code": "ME503", "name": "CAD/CAM", "type": "HEAVY"},
            {"code": "ME504", "name": "Industrial Engineering", "type": "NONMAJOR"},
            {"code": "OE501", "name": "Open Elective I", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE501", "name": "Design of RC Structures", "type": "HEAVY"},
            {"code": "CE502", "name": "Water Resources Engineering", "type": "HEAVY"},
            {"code": "CE503", "name": "Construction Management", "type": "HEAVY"},
            {"code": "CE504", "name": "Remote Sensing", "type": "NONMAJOR"},
            {"code": "OE501", "name": "Open Elective I", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE501", "name": "High Voltage Engineering", "type": "HEAVY"},
            {"code": "EE502", "name": "Switchgear & Protection", "type": "HEAVY"},
            {"code": "EE503", "name": "Electric Drives", "type": "HEAVY"},
            {"code": "EE504", "name": "Renewable Energy", "type": "NONMAJOR"},
            {"code": "OE501", "name": "Open Elective I", "type": "NONMAJOR"}
        ]
    },
    6: {  # Semester 6 (Even)
        101: [
            {"code": "CS601", "name": "Artificial Intelligence", "type": "HEAVY"},
            {"code": "CS602", "name": "Cloud Computing", "type": "HEAVY"},
            {"code": "CS603", "name": "Big Data Analytics", "type": "HEAVY"},
            {"code": "CS604", "name": "Mobile Computing", "type": "NONMAJOR"},
            {"code": "OE601", "name": "Open Elective II", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC601", "name": "Satellite Communication", "type": "HEAVY"},
            {"code": "EC602", "name": "Radar Engineering", "type": "HEAVY"},
            {"code": "EC603", "name": "Image Processing", "type": "HEAVY"},
            {"code": "EC604", "name": "Biomedical Electronics", "type": "NONMAJOR"},
            {"code": "OE601", "name": "Open Elective II", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME601", "name": "Refrigeration & AC", "type": "HEAVY"},
            {"code": "ME602", "name": "Robotics", "type": "HEAVY"},
            {"code": "ME603", "name": "Finite Element Analysis", "type": "HEAVY"},
            {"code": "ME604", "name": "Operations Research", "type": "NONMAJOR"},
            {"code": "OE601", "name": "Open Elective II", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE601", "name": "Steel Structures", "type": "HEAVY"},
            {"code": "CE602", "name": "Foundation Engineering", "type": "HEAVY"},
            {"code": "CE603", "name": "Traffic Engineering", "type": "HEAVY"},
            {"code": "CE604", "name": "Waste Management", "type": "NONMAJOR"},
            {"code": "OE601", "name": "Open Elective II", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE601", "name": "Power System Operation", "type": "HEAVY"},
            {"code": "EE602", "name": "Smart Grid", "type": "HEAVY"},
            {"code": "EE603", "name": "Power Quality", "type": "HEAVY"},
            {"code": "EE604", "name": "Energy Auditing", "type": "NONMAJOR"},
            {"code": "OE601", "name": "Open Elective II", "type": "NONMAJOR"}
        ]
    },
    7: {  # Semester 7 (Odd)
        101: [
            {"code": "CS701", "name": "Deep Learning", "type": "HEAVY"},
            {"code": "CS702", "name": "Blockchain Technology", "type": "HEAVY"},
            {"code": "CS703", "name": "Distributed Systems", "type": "HEAVY"},
            {"code": "CS704", "name": "Project Phase I", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC701", "name": "5G Technologies", "type": "HEAVY"},
            {"code": "EC702", "name": "Machine Learning for ECE", "type": "HEAVY"},
            {"code": "EC703", "name": "RF Circuit Design", "type": "HEAVY"},
            {"code": "EC704", "name": "Project Phase I", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME701", "name": "Additive Manufacturing", "type": "HEAVY"},
            {"code": "ME702", "name": "Vehicle Dynamics", "type": "HEAVY"},
            {"code": "ME703", "name": "Mechatronics", "type": "HEAVY"},
            {"code": "ME704", "name": "Project Phase I", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE701", "name": "Earthquake Engineering", "type": "HEAVY"},
            {"code": "CE702", "name": "Bridge Engineering", "type": "HEAVY"},
            {"code": "CE703", "name": "Urban Planning", "type": "HEAVY"},
            {"code": "CE704", "name": "Project Phase I", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE701", "name": "HVDC Transmission", "type": "HEAVY"},
            {"code": "EE702", "name": "AI in Power Systems", "type": "HEAVY"},
            {"code": "EE703", "name": "Electric Vehicles", "type": "HEAVY"},
            {"code": "EE704", "name": "Project Phase I", "type": "NONMAJOR"}
        ]
    },
    8: {  # Semester 8 (Even)
        101: [
            {"code": "CS801", "name": "Quantum Computing", "type": "HEAVY"},
            {"code": "CS802", "name": "Cybersecurity", "type": "HEAVY"},
            {"code": "CS803", "name": "Project Phase II", "type": "NONMAJOR"},
            {"code": "CS804", "name": "Seminar", "type": "NONMAJOR"}
        ],
        201: [
            {"code": "EC801", "name": "Quantum Electronics", "type": "HEAVY"},
            {"code": "EC802", "name": "Advanced DSP", "type": "HEAVY"},
            {"code": "EC803", "name": "Project Phase II", "type": "NONMAJOR"},
            {"code": "EC804", "name": "Seminar", "type": "NONMAJOR"}
        ],
        301: [
            {"code": "ME801", "name": "Advanced Manufacturing", "type": "HEAVY"},
            {"code": "ME802", "name": "Product Design", "type": "HEAVY"},
            {"code": "ME803", "name": "Project Phase II", "type": "NONMAJOR"},
            {"code": "ME804", "name": "Seminar", "type": "NONMAJOR"}
        ],
        401: [
            {"code": "CE801", "name": "Advanced Structures", "type": "HEAVY"},
            {"code": "CE802", "name": "Smart Cities", "type": "HEAVY"},
            {"code": "CE803", "name": "Project Phase II", "type": "NONMAJOR"},
            {"code": "CE804", "name": "Seminar", "type": "NONMAJOR"}
        ],
        501: [
            {"code": "EE801", "name": "Power System Planning", "type": "HEAVY"},
            {"code": "EE802", "name": "Advanced Control", "type": "HEAVY"},
            {"code": "EE803", "name": "Project Phase II", "type": "NONMAJOR"},
            {"code": "EE804", "name": "Seminar", "type": "NONMAJOR"}
        ]
    }
}


def generate_random_name():
    """Generate a random full name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def generate_regno(dept_code, year_of_joining, student_num):
    """Generate register number in format: MLID + DeptCode(3) + YearOfJoining(YY) + StudentCount(001-100)"""
    return f"MLID{dept_code}{year_of_joining:02d}{student_num:03d}"


def generate_student_email(regno):
    """Generate student email"""
    return f"{regno.lower()}@student.mlid.edu"


def generate_faculty_email(fac_num):
    """Generate faculty email"""
    return f"fac{fac_num:02d}@mlid.edu"


def setup_database():
    """Setup all collections and insert mock data"""
    db = get_db()
    
    print("Clearing existing data...")
    # Clear existing collections
    db.users.drop()
    db.departments.drop()
    db.subjects.drop()
    db.exam_halls.drop()
    db.exam_schedules.drop()
    db.seating_arrangements.drop()
    db.hall_tickets.drop()
    db.attendance.drop()
    db.authorizations.drop()
    db.exam_cycles.drop()
    
    print("Creating indexes...")
    # Create indexes
    db.users.create_index("email", unique=True)
    db.users.create_index("regno")
    db.users.create_index("role")
    db.subjects.create_index([("semester", 1), ("department", 1)])
    db.exam_schedules.create_index("exam_cycle_id")
    db.seating_arrangements.create_index("exam_cycle_id")
    db.attendance.create_index([("exam_cycle_id", 1), ("regno", 1)])
    
    # Insert Departments
    print("Inserting departments...")
    departments = []
    for dept_code in DEPARTMENTS:
        departments.append({
            "dept_code": dept_code,
            "name": DEPARTMENT_NAMES[dept_code]
        })
    db.departments.insert_many(departments)
    
    # Insert Subjects
    print("Inserting subjects...")
    subjects = []
    for semester, dept_subjects in SUBJECTS_DATA.items():
        for dept_code, subj_list in dept_subjects.items():
            for subj in subj_list:
                subjects.append({
                    "code": subj["code"],
                    "name": subj["name"],
                    "type": subj["type"],
                    "semester": semester,
                    "department": dept_code
                })
    db.subjects.insert_many(subjects)
    
    # Insert Students (2000 total)
    print("Inserting students...")
    students = []
    for year in range(1, 5):  # Years 1-4
        year_of_joining = YEAR_MAPPING[year]
        for dept_code in DEPARTMENTS:
            for student_num in range(1, STUDENTS_PER_DEPT_PER_YEAR + 1):
                regno = generate_regno(dept_code, year_of_joining, student_num)
                students.append({
                    "email": generate_student_email(regno),
                    "password": DEFAULT_PASSWORD,
                    "role": "student",
                    "regno": regno,
                    "name": generate_random_name(),
                    "department": dept_code,
                    "year": year,
                    "photo": "default_student.png"
                })
    db.users.insert_many(students)
    print(f"  Inserted {len(students)} students")
    
    # Insert Faculty (20 total)
    print("Inserting faculty...")
    faculty = []
    for fac_num in range(1, TOTAL_FACULTY + 1):
        dept_idx = (fac_num - 1) % len(DEPARTMENTS)
        faculty.append({
            "email": generate_faculty_email(fac_num),
            "password": DEFAULT_PASSWORD,
            "role": "faculty",
            "faculty_id": f"FAC{fac_num:02d}",
            "name": generate_random_name(),
            "department": DEPARTMENTS[dept_idx]
        })
    db.users.insert_many(faculty)
    print(f"  Inserted {len(faculty)} faculty members")
    
    # Insert COE
    print("Inserting COE...")
    db.users.insert_one({
        "email": "coe@exam.com",
        "password": DEFAULT_PASSWORD,
        "role": "coe",
        "name": "Controller of Examinations"
    })
    
    # Insert Exam Halls (20 total)
    print("Inserting exam halls...")
    halls = []
    for hall_num in range(1, TOTAL_HALLS + 1):
        bench_capacity = random.randint(MIN_BENCH_CAPACITY, MAX_BENCH_CAPACITY)
        columns = random.randint(MIN_COLUMNS, MAX_COLUMNS)
        halls.append({
            "hall_id": f"HALL{hall_num:02d}",
            "name": f"Examination Hall {hall_num}",
            "bench_capacity": bench_capacity,
            "columns": columns,
            "rows": (bench_capacity + columns - 1) // columns  # Calculate rows
        })
    db.exam_halls.insert_many(halls)
    print(f"  Inserted {len(halls)} exam halls")
    
    # Initialize authorizations collection
    print("Initializing authorizations...")
    db.authorizations.insert_one({
        "type": "global",
        "hall_ticket_enabled": False,
        "qr_scan_enabled": False
    })
    
    print("\nDatabase setup complete!")
    print(f"  Total students: {len(students)}")
    print(f"  Total faculty: {len(faculty)}")
    print(f"  Total halls: {len(halls)}")
    print(f"  Total departments: {len(DEPARTMENTS)}")
    
    # Print sample login credentials
    print("\n=== Sample Login Credentials ===")
    print("COE: coe@exam.com / password123")
    print("Faculty: fac01@mlid.edu / password123")
    print("Student (Year 1, Dept 101): mlid10125001@student.mlid.edu / password123")
    print("Student (Year 2, Dept 201): mlid20124050@student.mlid.edu / password123")


if __name__ == "__main__":
    setup_database()
