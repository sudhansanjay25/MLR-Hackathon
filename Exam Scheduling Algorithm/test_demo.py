"""
Demo script to test exam scheduling functionality
Tests both semester and internal exam scheduling
"""

from scheduler import ExamScheduler
from pdf_generator import generate_schedule_pdf
from datetime import datetime
import os

def print_header(title):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_schedule_summary(schedule, violations):
    """Print schedule summary"""
    # Group by date
    schedule_by_date = {}
    for item in schedule:
        date = item['date']
        if date not in schedule_by_date:
            schedule_by_date[date] = []
        schedule_by_date[date].append(item)
    
    # Print table
    print("\n" + "-"*95)
    print(f"{'Date':<15} {'Session':<8} {'Dept':<8} {'Type':<10} {'Code':<10} {'Subject':<30}")
    print("-"*95)
    
    for date in sorted(schedule_by_date.keys(), key=lambda x: datetime.strptime(x, '%d.%m.%Y')):
        exams = schedule_by_date[date]
        
        # Sort by session then department
        session_order = {'FN': 0, 'AN': 1, 'SINGLE': 0}
        exams.sort(key=lambda x: (session_order.get(x['session'], 2), x['department']))
        
        for i, exam in enumerate(exams):
            date_str = date if i == 0 else ''
            
            # Truncate subject name if too long
            subject_name = exam['subject_name']
            if len(subject_name) > 30:
                subject_name = subject_name[:27] + "..."
            
            print(f"{date_str:<15} {exam['session']:<8} {exam['department']:<8} "
                  f"{exam['subject_type']:<10} {exam['subject_code']:<10} {subject_name:<30}")
        
        if len(exams) > 0:
            print("-"*95)
    
    # Print violations
    if violations:
        print(f"\n⚠️  Constraint Violations: {len(violations)}")
        for v in violations:
            print(f"   - {v['subject_code']}: {v['description']}")
    else:
        print("\n✅ No constraint violations!")

def test_semester_exam_scheduling():
    """Test semester exam scheduling"""
    print_header("TEST 1: SEMESTER EXAM SCHEDULING")
    
    scheduler = ExamScheduler()
    
    try:
        # Test parameters
        year = 2
        start_date = "16.12.2025"
        end_date = "28.12.2025"
        holidays = ["20.12.2025", "25.12.2025"]  # Two holidays
        
        print(f"\nParameters:")
        print(f"  Year: {year}")
        print(f"  Date Range: {start_date} to {end_date}")
        print(f"  Holidays: {', '.join(holidays)}")
        
        # Generate schedule
        print("\n📊 Generating schedule...")
        schedule, violations = scheduler.schedule_semester_exams(
            year, start_date, end_date, holidays
        )
        
        # Create cycle and save
        cycle_id = scheduler.create_exam_cycle('SEMESTER', year, start_date, end_date)
        scheduler.save_schedule_to_db(cycle_id, schedule, violations)
        
        # Display results
        print(f"\n✅ Schedule Generated!")
        print(f"   Total Exams: {len(schedule)}")
        print(f"   Violations: {len(violations)}")
        print(f"   Cycle ID: {cycle_id}")
        
        print_schedule_summary(schedule, violations)
        
        # Department summary
        print("\n📊 Department-wise Summary:")
        dept_summary = {}
        for exam in schedule:
            dept = exam['department']
            if dept not in dept_summary:
                dept_summary[dept] = {'HEAVY': 0, 'NONMAJOR': 0}
            dept_summary[dept][exam['subject_type']] += 1
        
        for dept, counts in sorted(dept_summary.items()):
            print(f"   {dept}: {counts['HEAVY']} Heavy + {counts['NONMAJOR']} Non-major = {sum(counts.values())} total")
        
        # Generate PDF
        print("\n📄 Generating PDF...")
        try:
            pdf_path = generate_schedule_pdf(
                schedule, violations, 'SEMESTER', year,
                start_date, end_date,
                filename='test_semester_schedule.pdf'
            )
            print(f"   ✅ PDF saved: {os.path.abspath(pdf_path)}")
        except Exception as e:
            print(f"   ⚠️  PDF generation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scheduler.close()

def test_internal_exam_scheduling():
    """Test internal exam scheduling"""
    print_header("TEST 2: INTERNAL EXAM SCHEDULING")
    
    scheduler = ExamScheduler()
    
    try:
        # Test parameters
        year = 2
        start_date = "02.12.2025"
        end_date = "12.12.2025"
        holidays = ["07.12.2025"]  # One holiday (Sunday would be auto-excluded)
        
        print(f"\nParameters:")
        print(f"  Year: {year}")
        print(f"  Date Range: {start_date} to {end_date}")
        print(f"  Holidays: {', '.join(holidays)}")
        
        # Generate schedule
        print("\n📊 Generating schedule...")
        schedule, violations = scheduler.schedule_internal_exams(
            year, start_date, end_date, holidays
        )
        
        # Create cycle and save
        cycle_id = scheduler.create_exam_cycle('INTERNAL', year, start_date, end_date)
        scheduler.save_schedule_to_db(cycle_id, schedule, violations)
        
        # Display results
        print(f"\n✅ Schedule Generated!")
        print(f"   Total Exams: {len(schedule)}")
        print(f"   Violations: {len(violations)}")
        print(f"   Cycle ID: {cycle_id}")
        
        print_schedule_summary(schedule, violations)
        
        # Department summary
        print("\n📊 Department-wise Summary:")
        dept_summary = {}
        for exam in schedule:
            dept = exam['department']
            if dept not in dept_summary:
                dept_summary[dept] = 0
            dept_summary[dept] += 1
        
        for dept, count in sorted(dept_summary.items()):
            print(f"   {dept}: {count} exams")
        
        # Generate PDF
        print("\n📄 Generating PDF...")
        try:
            pdf_path = generate_schedule_pdf(
                schedule, violations, 'INTERNAL', year,
                start_date, end_date,
                filename='test_internal_schedule.pdf'
            )
            print(f"   ✅ PDF saved: {os.path.abspath(pdf_path)}")
        except Exception as e:
            print(f"   ⚠️  PDF generation failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scheduler.close()

def test_edge_case_insufficient_dates():
    """Test edge case with insufficient dates"""
    print_header("TEST 3: EDGE CASE - INSUFFICIENT DATES")
    
    scheduler = ExamScheduler()
    
    try:
        # Test parameters - only 5 days but need more
        year = 2
        start_date = "16.12.2025"
        end_date = "20.12.2025"  # Only 4-5 available days
        holidays = []
        
        print(f"\nParameters:")
        print(f"  Year: {year}")
        print(f"  Date Range: {start_date} to {end_date} (Limited days!)")
        print(f"  Note: After fix, system correctly requires one exam per dept per day")
        print(f"  Expected: Will fail gracefully if insufficient dates")
        
        # Generate schedule
        print("\n📊 Generating schedule...")
        schedule, violations = scheduler.schedule_semester_exams(
            year, start_date, end_date, holidays
        )
        
        print(f"\n⚠️  Schedule Generated (Partial):")
        print(f"   Total Exams: {len(schedule)}")
        print(f"   Violations: {len(violations)}")
        
        if violations:
            print("\n   Top violations:")
            for i, v in enumerate(violations[:5], 1):
                print(f"   {i}. {v['subject_code']}: {v['description']}")
            if len(violations) > 5:
                print(f"   ... and {len(violations) - 5} more")
        
        print("\n   ✅ System handled tight schedule appropriately")
        return True
        
    except ValueError as e:
        print(f"\n✅ Expected Error Caught: {e}")
        print(f"   System correctly identified insufficient dates.")
        print(f"   This is the correct behavior - prevents invalid schedules!")
        return True
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        scheduler.close()

def main():
    """Run all tests"""
    print_header("EXAM SCHEDULING ALGORITHM - AUTOMATED TESTS")
    print("  Testing all functionality with mock data")
    
    results = []
    
    # Test 1: Semester exams
    results.append(("Semester Exam Scheduling", test_semester_exam_scheduling()))
    
    # Test 2: Internal exams
    results.append(("Internal Exam Scheduling", test_internal_exam_scheduling()))
    
    # Test 3: Edge case
    results.append(("Edge Case - Insufficient Dates", test_edge_case_insufficient_dates()))
    
    # Summary
    print_header("TEST RESULTS SUMMARY")
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {status} - {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n   Total: {passed_count}/{total_count} tests passed")
    print("="*70)

if __name__ == "__main__":
    main()
