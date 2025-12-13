#!/usr/bin/env python3
"""
Quick test for bulk hall ticket generation
"""

import sys
from pathlib import Path
from pymongo import MongoClient

# Get latest schedule
client = MongoClient('mongodb://localhost:27017/')
db = client['exam_management']

# Find any schedule
schedule = db.schedules.find_one({})
if not schedule:
    print("No schedule found. Please run test_hall_ticket.py first.")
    sys.exit(1)

schedule_id = str(schedule['_id'])
print(f"Testing bulk generation with schedule: {schedule_id}")

# Import wrapper
sys.path.insert(0, str(Path(__file__).parent))
from hall_ticket_wrapper import MongoHallTicketGenerator

# Generate bulk
generator = MongoHallTicketGenerator(schedule_id)
result = generator.generate_bulk_hall_tickets(year=1)

print(f"\nResults:")
print(f"  Total: {result['total']}")
print(f"  Successful: {result['successful']}")
print(f"  Failed: {result['failed']}")

if result['generated']:
    print(f"\nGenerated hall tickets:")
    for ticket in result['generated']:
        print(f"  - {ticket['registerNumber']}: {ticket['pdfPath']}")

generator.close()
client.close()
