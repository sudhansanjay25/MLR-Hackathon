import csv
import random

# --- Configuration ---
FILENAME = "student_database.csv"
DEFAULT_CODE = "7140"

# Mapping Years to "Join Year" suffix
# Assuming current academic year involves these batches:
# 4th Year = Joined 2022
# 3rd Year = Joined 2023
# 2nd Year = Joined 2024
# 1st Year = Joined 2025
year_batch_map = {
    "1": "25",
    "2": "24",
    "3": "23",
    "4": "22"
}

# 5 Departments with arbitrary 3-digit codes
departments = {
    "CSE": "104",
    "ECE": "106",
    "MECH": "114",
    "CIVIL": "103",
    "EEE": "105"
}

# Sample names to mix and match for realistic "Name" generation
first_names = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Saanvi", "Myra", "Riya", "Anvi", "Sarah"]
last_names = ["Sharma", "Verma", "Gupta", "Malhotra", "Bhat", "Saxena", "Mehta", "Jain", "Singh", "Yadav", "Das", "Rao", "Nair", "Patel", "Reddy", "Chopra", "Desai", "Joshi", "Kapoor", "Kumar"]

def generate_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# --- Data Generation ---
data_rows = []

print("Generating data...")

for dept_name, dept_code in departments.items():
    for year_study, join_year in year_batch_map.items():
        
        # Randomize number of students between 100 and 150
        num_students = random.randint(100, 150)
        
        for i in range(1, num_students + 1):
            # Generate Name
            name = generate_name()
            
            # Format Roll Number (e.g., 001, 015, 120)
            roll_number_str = f"{i:03d}"
            
            # Construct Register Number
            # Format: 7140 + YY + DDD + NNN
            reg_number = f"{DEFAULT_CODE}{join_year}{dept_code}{roll_number_str}"
            
            # Add to list
            data_rows.append([name, reg_number, dept_name, year_study])

# --- Write to CSV ---
header = ["Name", "Register Number", "Department", "Year of Study"]

with open(FILENAME, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(header)
    writer.writerows(data_rows)

print(f"Success! '{FILENAME}' has been created with {len(data_rows)} students.")