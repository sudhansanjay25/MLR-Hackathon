"""
Clear all exam schedules and cycles from database
Run this before testing new schedules
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'exam_scheduling.db')

def clear_all_schedules():
    """Clear all schedules, cycles, and seating allocations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get counts before clearing
        cursor.execute('SELECT COUNT(*) FROM schedules')
        schedule_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM exam_cycles')
        cycle_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM seating_allocations')
        allocation_count = cursor.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("CLEARING EXAM SCHEDULES")
        print("=" * 60)
        print(f"\nBefore clearing:")
        print(f"  • Schedules: {schedule_count}")
        print(f"  • Exam Cycles: {cycle_count}")
        print(f"  • Seating Allocations: {allocation_count}")
        
        # Clear all tables
        cursor.execute('DELETE FROM seating_allocations')
        cursor.execute('DELETE FROM schedules')
        cursor.execute('DELETE FROM exam_cycles')
        
        conn.commit()
        
        # Verify clearing
        cursor.execute('SELECT COUNT(*) FROM schedules')
        remaining_schedules = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM exam_cycles')
        remaining_cycles = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM seating_allocations')
        remaining_allocations = cursor.fetchone()[0]
        
        print(f"\n✅ Successfully cleared!")
        print(f"\nAfter clearing:")
        print(f"  • Schedules: {remaining_schedules}")
        print(f"  • Exam Cycles: {remaining_cycles}")
        print(f"  • Seating Allocations: {remaining_allocations}")
        print("\n" + "=" * 60)
        print("Ready to create new schedules!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error clearing schedules: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clear_all_schedules()
