"""
Test vertical line separator in Internal exam
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seating_allocation import SeatingAllocationSystem

script_dir = os.path.dirname(os.path.abspath(__file__))
halls_file = os.path.join(script_dir, 'halls.csv')
students_file = os.path.join(script_dir, 'year1.csv')
teachers_file = os.path.join(script_dir, 'Teachers.csv')

print("\n" + "=" * 60)
print("Testing Internal Exam with VERTICAL Line Separator")
print("=" * 60)

system = SeatingAllocationSystem(halls_file, students_file, teachers_file, 
                                 session='FN', exam_type='Internal', year=1)

allocations = system.allocate_seats_mixed_department()
system.assign_teachers()

student_pdf = system.generate_student_pdf()

print(f"\n✓ Generated: {student_pdf}")
print("\nVerify in the PDF:")
print("  • Students shown side-by-side (left and right)")
print("  • A VERTICAL line separates the two students")
print("  • No '|' text character visible")
print("\n" + "=" * 60)
