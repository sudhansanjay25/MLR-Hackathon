"""
Quick Reference Guide for Exam Scheduling System
Examples of how to use the scheduler programmatically
"""

from scheduler import ExamScheduler

# ============================================================================
# EXAMPLE 1: Schedule Semester Exams
# ============================================================================

def example_semester_scheduling():
    """Example: Schedule semester exams for Year 2"""
    
    # Initialize scheduler
    scheduler = ExamScheduler('exam_scheduling.db')
    
    # Define parameters
    year = 2
    start_date = "16.12.2025"
    end_date = "28.12.2025"
    holidays = ["20.12.2025", "25.12.2025"]
    
    # Generate schedule
    schedule, violations = scheduler.schedule_semester_exams(
        year, start_date, end_date, holidays
    )
    
    # Save to database
    cycle_id = scheduler.create_exam_cycle('SEMESTER', year, start_date, end_date)
    scheduler.save_schedule_to_db(cycle_id, schedule, violations)
    
    # Access results
    print(f"Scheduled {len(schedule)} exams")
    print(f"Violations: {len(violations)}")
    
    # Retrieve schedule from database
    saved_schedule = scheduler.get_schedule(cycle_id)
    saved_violations = scheduler.get_violations(cycle_id)
    
    scheduler.close()
    return cycle_id

# ============================================================================
# EXAMPLE 2: Schedule Internal Exams
# ============================================================================

def example_internal_scheduling():
    """Example: Schedule internal exams for Year 2"""
    
    scheduler = ExamScheduler('exam_scheduling.db')
    
    # Define parameters
    year = 2
    start_date = "02.12.2025"
    end_date = "12.12.2025"
    holidays = ["07.12.2025"]
    
    # Generate schedule
    schedule, violations = scheduler.schedule_internal_exams(
        year, start_date, end_date, holidays
    )
    
    # Save to database
    cycle_id = scheduler.create_exam_cycle('INTERNAL', year, start_date, end_date)
    scheduler.save_schedule_to_db(cycle_id, schedule, violations)
    
    scheduler.close()
    return cycle_id

# ============================================================================
# EXAMPLE 3: Query Schedule by Department
# ============================================================================

def example_query_by_department(cycle_id, department):
    """Example: Get schedule for specific department"""
    
    scheduler = ExamScheduler('exam_scheduling.db')
    
    # Get full schedule
    full_schedule = scheduler.get_schedule(cycle_id)
    
    # Filter by department
    dept_schedule = [
        exam for exam in full_schedule 
        if exam['department'] == department
    ]
    
    # Print department schedule
    print(f"\n{department} Exam Schedule:")
    print("-" * 70)
    for exam in dept_schedule:
        print(f"{exam['date']:<15} {exam['session']:<8} {exam['subject_code']:<10} {exam['subject_name']}")
    
    scheduler.close()
    return dept_schedule

# ============================================================================
# EXAMPLE 4: Check Available Dates
# ============================================================================

def example_check_available_dates():
    """Example: Calculate available dates before scheduling"""
    
    scheduler = ExamScheduler('exam_scheduling.db')
    
    start_date = "16.12.2025"
    end_date = "28.12.2025"
    holidays = ["20.12.2025", "25.12.2025"]
    
    # Get available dates
    available_dates = scheduler.generate_available_dates(
        start_date, end_date, holidays
    )
    
    print(f"\nAvailable dates: {len(available_dates)}")
    print(f"For semester: {len(available_dates) * 2} slots (FN + AN)")
    print(f"For internal: {len(available_dates)} slots")
    
    print("\nDates:")
    for date in available_dates:
        print(f"  - {date}")
    
    scheduler.close()
    return available_dates

# ============================================================================
# EXAMPLE 5: Custom Scheduling with Manual Control
# ============================================================================

def example_custom_scheduling():
    """Example: Access scheduling components for custom logic"""
    
    scheduler = ExamScheduler('exam_scheduling.db')
    
    # Get subjects
    subjects = scheduler.get_subjects_for_year(year=2, exam_type='SEMESTER')
    
    print(f"\nSubjects for Year 2:")
    for subject in subjects:
        print(f"  {subject['subject_code']}: {subject['subject_name']} "
              f"[{subject['department']}, {subject['subject_type']}]")
    
    # Build conflict graph
    conflicts = scheduler.build_conflict_graph(subjects)
    
    print(f"\nConflict Graph:")
    for subject_id, conflicting_ids in list(conflicts.items())[:3]:
        print(f"  Subject {subject_id} conflicts with {len(conflicting_ids)} others")
    
    scheduler.close()

# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("  EXAM SCHEDULER - PROGRAMMATIC USAGE EXAMPLES")
    print("="*70)
    
    # Example 1: Schedule semester exams
    print("\n[1] Scheduling Semester Exams...")
    cycle_id_sem = example_semester_scheduling()
    print(f"    Created cycle ID: {cycle_id_sem}")
    
    # Example 2: Schedule internal exams
    print("\n[2] Scheduling Internal Exams...")
    cycle_id_int = example_internal_scheduling()
    print(f"    Created cycle ID: {cycle_id_int}")
    
    # Example 3: Query by department
    print("\n[3] Querying CSE Department Schedule...")
    example_query_by_department(cycle_id_sem, 'CSE')
    
    # Example 4: Check available dates
    print("\n[4] Checking Available Dates...")
    example_check_available_dates()
    
    # Example 5: Custom scheduling
    print("\n[5] Custom Scheduling Components...")
    example_custom_scheduling()
    
    print("\n" + "="*70)
    print("  All examples completed!")
    print("="*70)
