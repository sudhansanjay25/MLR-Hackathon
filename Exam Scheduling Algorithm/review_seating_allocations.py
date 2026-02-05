"""
Query Tool: Review Saved Seating Allocations from Database
"""

import sqlite3
import pandas as pd

DB_PATH = 'exam_scheduling.db'

def view_all_allocations():
    """Show all saved seating allocations"""
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT 
            exam_date, session, cycle_id,
            COUNT(*) as students,
            COUNT(DISTINCT hall_id) as halls,
            COUNT(DISTINCT department) as departments
        FROM seating_allocations
        GROUP BY exam_date, session, cycle_id
        ORDER BY exam_date, session
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("\n" + "="*80)
    print("📋 ALL SAVED SEATING ALLOCATIONS")
    print("="*80)
    
    if df.empty:
        print("\n⚠️ No allocations found in database")
    else:
        print(f"\n✅ Found {len(df)} allocation(s):\n")
        print(df.to_string(index=False))
    
    return df


def view_allocation_by_date(exam_date, session):
    """View detailed allocation for a specific date"""
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT 
            hall_name, seat_no, reg_no, student_name, department, bench_number
        FROM seating_allocations
        WHERE exam_date = ? AND session = ?
        ORDER BY hall_name, bench_number, seat_no
    '''
    
    df = pd.read_sql_query(query, conn, params=(exam_date, session))
    conn.close()
    
    print("\n" + "="*80)
    print(f"📖 SEATING ALLOCATION: {exam_date} {session}")
    print("="*80)
    
    if df.empty:
        print(f"\n⚠️ No allocation found for {exam_date} {session}")
    else:
        print(f"\n✅ Total students: {len(df)}")
        print(f"   Halls used: {df['hall_name'].nunique()}")
        print(f"   Departments: {', '.join(df['department'].unique())}")
        
        print("\n📊 Hall-wise Summary:")
        hall_summary = df.groupby('hall_name').agg({
            'reg_no': 'count',
            'department': lambda x: len(x.unique())
        }).rename(columns={'reg_no': 'Students', 'department': 'Departments'})
        
        for hall, row in hall_summary.iterrows():
            print(f"   {hall}: {row['Students']} students, {row['Departments']} departments")
        
        print("\n📋 Sample Allocations (first 20):")
        print(df.head(20).to_string(index=False))
    
    return df


def view_hall_details(exam_date, session, hall_name):
    """View all students in a specific hall"""
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT 
            seat_no, reg_no, student_name, department, bench_number
        FROM seating_allocations
        WHERE exam_date = ? AND session = ? AND hall_name = ?
        ORDER BY bench_number, seat_no
    '''
    
    df = pd.read_sql_query(query, conn, params=(exam_date, session, hall_name))
    conn.close()
    
    print("\n" + "="*80)
    print(f"🏛️ HALL DETAILS: {hall_name} ({exam_date} {session})")
    print("="*80)
    
    if df.empty:
        print(f"\n⚠️ No allocation found for {hall_name}")
    else:
        print(f"\n✅ Students in this hall: {len(df)}")
        print(f"   Departments: {', '.join(df['department'].unique())}")
        
        print("\n📋 Complete Hall Allocation:")
        print(df.to_string(index=False))
    
    return df


def view_student_seat(exam_date, session, reg_no):
    """Find where a specific student is seated"""
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT 
            hall_name, seat_no, bench_number, student_name, department
        FROM seating_allocations
        WHERE exam_date = ? AND session = ? AND reg_no = ?
    '''
    
    df = pd.read_sql_query(query, conn, params=(exam_date, session, reg_no))
    conn.close()
    
    print("\n" + "="*80)
    print(f"🔍 STUDENT SEAT LOOKUP: {reg_no}")
    print("="*80)
    
    if df.empty:
        print(f"\n⚠️ Student {reg_no} not found in allocation for {exam_date} {session}")
    else:
        row = df.iloc[0]
        print(f"\n✅ Student: {row['student_name']} ({row['department']})")
        print(f"   Hall: {row['hall_name']}")
        print(f"   Seat: {row['seat_no']}")
        print(f"   Bench: {row['bench_number']}")
    
    return df


def view_department_distribution(exam_date, session):
    """View how departments are distributed across halls"""
    conn = sqlite3.connect(DB_PATH)
    
    query = '''
        SELECT 
            hall_name, department, COUNT(*) as count
        FROM seating_allocations
        WHERE exam_date = ? AND session = ?
        GROUP BY hall_name, department
        ORDER BY hall_name, department
    '''
    
    df = pd.read_sql_query(query, conn, params=(exam_date, session))
    conn.close()
    
    print("\n" + "="*80)
    print(f"📊 DEPARTMENT DISTRIBUTION: {exam_date} {session}")
    print("="*80)
    
    if df.empty:
        print(f"\n⚠️ No allocation found")
    else:
        # Pivot for better view
        pivot = df.pivot(index='hall_name', columns='department', values='count').fillna(0).astype(int)
        
        print("\n✅ Students per Department per Hall:")
        print(pivot.to_string())
        
        print("\n📊 Department Totals:")
        totals = df.groupby('department')['count'].sum().sort_values(ascending=False)
        for dept, count in totals.items():
            print(f"   {dept}: {count} students")
    
    return df


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*80)
    print("🔍 SEATING ALLOCATION QUERY TOOL")
    print("="*80)
    
    # Show all allocations
    all_allocations = view_all_allocations()
    
    if not all_allocations.empty:
        # Example: View first allocation in detail
        first_date = all_allocations.iloc[0]['exam_date']
        first_session = all_allocations.iloc[0]['session']
        
        print("\n" + "="*80)
        print("📖 Detailed view of first allocation:")
        print("="*80)
        
        # View allocation details
        allocation = view_allocation_by_date(first_date, first_session)
        
        if not allocation.empty:
            # View first hall details
            first_hall = allocation.iloc[0]['hall_name']
            view_hall_details(first_date, first_session, first_hall)
            
            # View first student
            first_student = allocation.iloc[0]['reg_no']
            view_student_seat(first_date, first_session, first_student)
            
            # View department distribution
            view_department_distribution(first_date, first_session)
    
    print("\n" + "="*80)
    print("💡 You can import this module and use these functions:")
    print("="*80)
    print("""
from review_seating_allocations import *

# View all allocations
view_all_allocations()

# View specific date
view_allocation_by_date('02.02.2026', 'AN')

# View specific hall
view_hall_details('02.02.2026', 'AN', 'Hall 1')

# Find student seat
view_student_seat('02.02.2026', 'AN', '24MLID05001')

# View department distribution
view_department_distribution('02.02.2026', 'AN')
    """)
