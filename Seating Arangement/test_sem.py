"""Test script for SEM exam type"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seating_allocation import SeatingAllocationSystem

# File paths
script_dir = os.path.dirname(os.path.abspath(__file__))
halls_file = os.path.join(script_dir, 'halls.csv')
students_file = os.path.join(script_dir, 'year1.csv')
teachers_file = os.path.join(script_dir, 'Teachers.csv')
output_file = os.path.join(script_dir, 'first_year_seating_allocation.xlsx')

print("\n" + "=" * 60)
print("TESTING SEM EXAM ALLOCATION")
print("=" * 60)

# Create allocation system for SEM
system = SeatingAllocationSystem(halls_file, students_file, teachers_file, 
                                 session='FN', exam_type='SEM')

print("\nGenerating seating arrangement for SEM Exam (FN session)...")
print("Mode: 1 student per bench (individual seating)")

# Perform allocation
allocations = system.allocate_seats_mixed_department()

# Assign teachers
system.assign_teachers()

# Generate Excel report
system.generate_excel_report(output_file)

# Generate PDF reports
student_pdf = system.generate_student_pdf()
faculty_pdf = system.generate_faculty_pdf()

# Print statistics
system.print_statistics()

print("\n" + "=" * 60)
print("SEM EXAM TEST COMPLETE!")
print("=" * 60)
print(f"\nExam Type: SEM")
print(f"Session: FN")
print(f"\nGenerated Files:")
print(f"  1. Excel Report: {output_file}")
print(f"  2. Student PDF: {student_pdf}")
print(f"  3. Faculty PDF: {faculty_pdf}")
print("\n")
