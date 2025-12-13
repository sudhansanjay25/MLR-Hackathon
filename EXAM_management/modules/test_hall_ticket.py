#!/usr/bin/env python3
"""
Test script for Hall Ticket Generation
Creates test data and generates a sample hall ticket
"""

import sys
from pathlib import Path
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from hall_ticket_wrapper import MongoHallTicketGenerator


def setup_test_data():
    """Create test schedule and student"""
    client = MongoClient('mongodb://localhost:27017/')
    db = client['exam_management']
    
    # Create test schedule
    schedule = {
        '_id': ObjectId(),
        'academicYear': '2024-25',
        'examType': 'SEM',
        'year': 1,
        'semester': 'END SEMESTER EXAMINATION – APR 2025',
        'session': 'FN',
        'startDate': datetime(2025, 5, 1),
        'endDate': datetime(2025, 5, 15),
        'timetable': [
            {
                'year': 1,
                'semester': 1,
                'subjectCode': '21CS101',
                'subjectName': 'Programming in C',
                'date': '01.05.2025',
                'session': 'FN'
            },
            {
                'year': 1,
                'semester': 1,
                'subjectCode': '21CS102',
                'subjectName': 'Data Structures',
                'date': '03.05.2025',
                'session': 'FN'
            },
            {
                'year': 1,
                'semester': 1,
                'subjectCode': '21CS103',
                'subjectName': 'Digital Logic',
                'date': '05.05.2025',
                'session': 'AN'
            }
        ],
        'createdAt': datetime.now()
    }
    
    # Insert or update schedule
    db.schedules.update_one(
        {'_id': schedule['_id']},
        {'$set': schedule},
        upsert=True
    )
    
    # Create test student (use existing one if available)
    student = {
        'registerNumber': 'TEST001',
        'name': 'Test Student',
        'studentName': 'Test Student',
        'degree': 'B.Tech',
        'branch': 'Computer Science and Engineering',
        'yearOfStudy': 1,
        'year': 1,
        'semester': 1,
        'sem': 1,
        'dateOfBirth': datetime(2005, 1, 15),
        'gender': 'Male',
        'regulation': 'R21'
    }
    
    # Insert or update student
    db.students.update_one(
        {'registerNumber': 'TEST001'},
        {'$set': student},
        upsert=True
    )
    
    print(f"✅ Test data created:")
    print(f"   Schedule ID: {schedule['_id']}")
    print(f"   Student: {student['registerNumber']} - {student['name']}")
    print()
    
    client.close()
    return str(schedule['_id']), student['registerNumber']


def test_hall_ticket_generation():
    """Test hall ticket generation"""
    print("=" * 60)
    print("Hall Ticket Generation Test")
    print("=" * 60)
    print()
    
    # Setup test data
    schedule_id, register_number = setup_test_data()
    
    # Generate hall ticket
    print(f"🔧 Generating hall ticket...")
    print(f"   Schedule ID: {schedule_id}")
    print(f"   Register Number: {register_number}")
    print()
    
    try:
        generator = MongoHallTicketGenerator(schedule_id)
        
        # Generate PDF
        pdf_path = generator.generate_hall_ticket_pdf(register_number)
        
        print(f"✅ Hall ticket generated successfully!")
        print(f"   PDF saved to: {pdf_path}")
        print()
        
        # Check if file exists
        if Path(pdf_path).exists():
            file_size = Path(pdf_path).stat().st_size
            print(f"   File size: {file_size:,} bytes")
            print()
            print("✅ Test PASSED!")
        else:
            print("❌ Test FAILED: PDF file not found")
            
        generator.close()
        
    except Exception as e:
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == '__main__':
    success = test_hall_ticket_generation()
    sys.exit(0 if success else 1)
