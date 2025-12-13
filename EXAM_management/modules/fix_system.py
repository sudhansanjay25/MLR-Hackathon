"""
Fix System Issues:
1. Update hall capacities to 30-35 benches
2. Already fixed seating algorithm in seating_wrapper.py
3. Need to check scheduler for all departments
"""
from pymongo import MongoClient
import random

# MongoDB connection
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['exam_management']

print("=" * 60)
print("FIXING SYSTEM ISSUES")
print("=" * 60)

# Issue 1: Fix hall capacities (30-35 benches, not 60-72-84)
print("\n1. Fixing hall capacities...")
halls = list(db.halls.find())

for hall in halls:
    # Assign random capacity between 30-35 benches
    new_capacity = random.randint(30, 35)
    db.halls.update_one(
        {'_id': hall['_id']},
        {'$set': {'capacity': new_capacity}}
    )
    print(f"   {hall['hallNumber']}: {hall['capacity']} -> {new_capacity} benches")

print(f"\n✅ Updated {len(halls)} halls to 30-35 bench capacity")

# Verify
print("\n2. Verifying hall capacities...")
updated_halls = list(db.halls.find({}, {'hallNumber': 1, 'capacity': 1}).sort('hallNumber', 1))
for h in updated_halls[:10]:  # Show first 10
    print(f"   {h['hallNumber']}: {h['capacity']} benches")
print(f"   ... ({len(updated_halls)} total halls)")

print("\n" + "=" * 60)
print("SYSTEM FIXES COMPLETED")
print("=" * 60)
print("\nNext steps:")
print("1. Hall capacities fixed ✅")
print("2. Seating algorithm fixed ✅")
print("3. Check scheduler for all department schedules")
print("4. Test PDF text wrapping")

client.close()
