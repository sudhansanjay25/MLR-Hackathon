from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from db import students_col, schedules_col, seating_col
import random

class SeatingManager:
    def __init__(self):
        # Mock Halls
        self.halls = [
            {'name': 'Hall-101', 'capacity': 30},
            {'name': 'Hall-102', 'capacity': 30},
            {'name': 'Hall-103', 'capacity': 30},
            {'name': 'Hall-104', 'capacity': 30},
            {'name': 'Hall-201', 'capacity': 30},
            {'name': 'Hall-202', 'capacity': 30},
        ]

    def generate_seating(self, date: str, session: str):
        # 1. Get exams for this slot
        exams = list(schedules_col.find({'date': date, 'session': session}))
        if not exams:
             raise ValueError("No exams scheduled for this slot")
        
        # 2. Get students involved
        # Group students by Department to mix them
        dept_students = {}
        for exam in exams:
            dept = exam['department']
            year = exam['year']
            sem = exam['semester']
            
            students = list(students_col.find({
                'department': dept, 
                'year': int(year), 
                'semester': int(sem)
            }))
            
            # Sort by RegNo
            students.sort(key=lambda x: x['register_number'])
            dept_students[dept] = students

        # 3. Alloction Logic (Linear Mixing)
        # Round robin fetch from departments
        allocations = []
        
        depts = list(dept_students.keys())
        max_len = max([len(s) for s in dept_students.values()])
        
        flat_student_list = []
        for i in range(max_len):
            for dept in depts:
                if i < len(dept_students[dept]):
                    flat_student_list.append(dept_students[dept][i])
        
        # Distribute to Halls
        student_idx = 0
        allocated_count = 0
        
        seating_records = []
        
        for hall in self.halls:
            if student_idx >= len(flat_student_list):
                break
                
            capacity = hall['capacity']
            
            for seat in range(1, capacity + 1):
                if student_idx >= len(flat_student_list):
                    break
                
                student = flat_student_list[student_idx]
                
                record = {
                    'hall': hall['name'],
                    'seat_no': seat,
                    'student_name': student['name'],
                    'register_number': student['register_number'],
                    'department': student['department'],
                    'exam_date': date,
                    'session': session
                }
                seating_records.append(record)
                student_idx += 1
        
        # Save to DB
        # Remove old allocation for this slot
        seating_col.delete_many({'exam_date': date, 'session': session})
        if seating_records:
            seating_col.insert_many(seating_records)
            
        return len(seating_records)

    def generate_pdf(self, date: str, session: str, output_path: str):
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        records = list(seating_col.find({'exam_date': date, 'session': session}).sort([('hall', 1), ('seat_no', 1)]))
        
        if not records:
             return False

        elements.append(Paragraph(f"Seating Arrangement - {date} ({session})", styles['Title']))
        elements.append(Spacer(1, 12))
        
        table_data = [['Hall', 'Seat', 'Reg No', 'Name', 'Dept']]
        
        for r in records:
            table_data.append([
                r['hall'], str(r['seat_no']), r['register_number'], r['student_name'], r['department']
            ])
            
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        return True
