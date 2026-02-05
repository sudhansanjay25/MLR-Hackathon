from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "exam_management_system"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
students_col = db['students']
subjects_col = db['subjects']
departments_col = db['departments']
exams_col = db['exams']
schedules_col = db['schedules']
seating_col = db['seating']
attendance_col = db['attendance']
users_col = db['users']

def init_db():
    """Check connection"""
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    init_db()
