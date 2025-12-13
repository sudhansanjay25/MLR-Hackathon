#!/usr/bin/env python
"""
Wrapper script for seating arrangement that accepts command-line arguments
and outputs JSON results
"""

import sys
import os
import json
import argparse
from seating_allocation import SeatingAllocationSystem

def main():
    parser = argparse.ArgumentParser(description='Generate seating arrangement for exams')
    parser.add_argument('--year', type=int, required=True, help='Academic year (1-4)')
    parser.add_argument('--exam-type', type=str, required=True, 
                       choices=['Internal1', 'Internal2', 'SEM'], 
                       help='Exam type')
    parser.add_argument('--session', type=str, default='FN', 
                       choices=['FN', 'AN', 'Morning'],
                       help='Exam session')
    parser.add_argument('--halls-file', type=str, default='halls.csv',
                       help='Path to halls CSV file')
    parser.add_argument('--students-file', type=str, required=True,
                       help='Path to students CSV file')
    parser.add_argument('--teachers-file', type=str, default='Teachers.csv',
                       help='Path to teachers CSV file')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for PDFs')
    
    args = parser.parse_args()
    
    try:
        # Determine internal number if Internal exam
        internal_number = 1
        if args.exam_type == 'Internal1':
            internal_number = 1
            exam_type = 'Internal'
        elif args.exam_type == 'Internal2':
            internal_number = 2
            exam_type = 'Internal'
        else:
            exam_type = 'SEM'
        
        # Create seating system
        system = SeatingAllocationSystem(
            halls_file=args.halls_file,
            students_file=args.students_file,
            teachers_file=args.teachers_file,
            session=args.session,
            exam_type=exam_type,
            year=args.year,
            internal_number=internal_number
        )
        
        # Generate allocation
        print(f"Generating seating for Year {args.year} - {args.exam_type}", file=sys.stderr)
        allocations = system.allocate_seats_mixed_department()
        
        # Assign teachers
        system.assign_teachers()
        
        # Generate PDFs
        student_pdf = system.generate_student_pdf()
        faculty_pdf = system.generate_faculty_pdf()
        
        # Print statistics
        system.print_statistics()
        
        # Prepare result as JSON
        result = {
            'success': True,
            'message': 'Seating arrangement generated successfully',
            'data': {
                'totalStudents': len(allocations),
                'hallsUsed': len(system.hall_wise_allocations),
                'studentPdfPath': student_pdf,
                'facultyPdfPath': faculty_pdf,
                'allocations': []
            }
        }
        
        # Add allocation details
        for _, row in allocations.iterrows():
            result['data']['allocations'].append({
                'hallNo': int(row['Hall No']),
                'seatNo': int(row['Seat No']),
                'registerNumber': str(row['Register Number']),
                'department': str(row['Department'])
            })
        
        # Output JSON result
        print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        error_result = {
            'success': False,
            'message': str(e),
            'error': str(type(e).__name__)
        }
        print(json.dumps(error_result, indent=2))
        return 1

if __name__ == '__main__':
    sys.exit(main())
