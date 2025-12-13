#!/usr/bin/env python
"""
MongoDB-Integrated Seating Allocation Wrapper
Preserves exact original PDF format using matplotlib while working with MongoDB database
"""

import sys
import json
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors

# MongoDB connection
MONGO_URI = "mongodb://127.0.0.1:27017/"
DB_NAME = "exam_management"

class MongoSeatingAllocator:
    """MongoDB-integrated seating allocator that generates PDFs matching original format"""
    
    def __init__(self, schedule_id, schedule_data=None):
        """Initialize with MongoDB schedule ID and optional schedule data"""
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.schedule_id = ObjectId(schedule_id) if isinstance(schedule_id, str) else schedule_id
        self.schedule_data = schedule_data  # Optional data from backend
        
        # Load schedule data
        self.load_schedule_data()
    
    def load_schedule_data(self):
        """Load schedule, allocations, halls, departments from MongoDB"""
        # Try to get schedule from MongoDB
        schedule = self.db.schedules.find_one({'_id': self.schedule_id})
        
        # If not found in DB, MUST get from allocations or schedule_data
        if not schedule:
            # First priority: check allocations
            alloc_count = self.db.allocations.count_documents({'schedule': self.schedule_id})
            if alloc_count > 0:
                # Build schedule from allocations - use defaults for PDF generation
                schedule = {
                    '_id': self.schedule_id,
                    'examType': 'Internal2',  # Default, will work for PDF
                    'yearOfStudy': 1,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'session': 'Morning'
                }
            elif self.schedule_data:
                # Use data passed from backend
                schedule = {
                    '_id': self.schedule_id,
                    'examType': self.schedule_data.get('examType', 'Internal2'),
                    'yearOfStudy': self.schedule_data.get('year', 1),
                    'date': self.schedule_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                    'session': self.schedule_data.get('session', 'Morning')
                }
            else:
                # Last resort: create minimal schedule for PDF generation
                schedule = {
                    '_id': self.schedule_id,
                    'examType': 'Internal2',
                    'yearOfStudy': 1,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'session': 'Morning'
                }
        
        self.schedule = schedule
        exam_type_raw = schedule['examType']
        
        # Handle examType formats: "Internal", "Internal1", "Internal2", "SEM"
        if 'Internal' in exam_type_raw:
            self.exam_type = 'Internal'
            # Extract internal number from "Internal1" or "Internal2"
            if exam_type_raw == 'Internal1':
                self.internal_number = 1
            elif exam_type_raw == 'Internal2':
                self.internal_number = 2
            else:
                self.internal_number = schedule.get('internalExamNumber', 1)
        else:
            self.exam_type = exam_type_raw
            self.internal_number = None
        
        self.year = schedule['yearOfStudy']
        self.generation_date = schedule.get('date', datetime.now().strftime('%Y-%m-%d'))
        self.session = schedule.get('session', 'FN')
        
        # Get all allocations for this schedule
        allocations = list(self.db.allocations.find({'schedule': self.schedule_id}).sort('seatNumber', 1))
        self.allocations = allocations
        
        # Group by hall
        self.hall_wise_allocations = {}
        hall_ids = set()
        
        for alloc in allocations:
            hall_id = alloc['hall']
            hall_ids.add(hall_id)
            
            if hall_id not in self.hall_wise_allocations:
                self.hall_wise_allocations[hall_id] = []
            
            self.hall_wise_allocations[hall_id].append(alloc)
        
        # Load hall information
        self.halls = {}
        for hall_id in hall_ids:
            hall = self.db.halls.find_one({'_id': hall_id})
            if hall:
                self.halls[hall_id] = hall
        
        # Load department names
        self.departments = {}
        dept_ids = set(alloc.get('department') for alloc in allocations if alloc.get('department'))
        for dept_id in dept_ids:
            dept = self.db.departments.find_one({'_id': dept_id})
            if dept:
                self.departments[dept_id] = dept['name']
    
    def _convert_to_2d_layout(self, hall_allocations, hall_info):
        """Convert flat allocations to 2D grid layout matching exact column structure"""
        num_cols = hall_info.get('numberOfColumns', 4)
        rows_per_col = hall_info.get('rowsPerColumn', 15)
        
        # Initialize empty grid
        layout = [['-' for _ in range(num_cols)] for _ in range(rows_per_col)]
        
        # Department counter
        dept_counts = {}
        
        if self.exam_type == 'SEM':
            # SEM: One student per cell, fill column by column
            for alloc in hall_allocations:
                seat_num = alloc['seatNumber'] - 1  # 0-indexed
                col = seat_num // rows_per_col
                row = seat_num % rows_per_col
                
                if col < num_cols and row < rows_per_col:
                    reg_no = alloc.get('registerNumber', '-')
                    layout[row][col] = reg_no
                    
                    # Count department
                    dept_id = alloc.get('department')
                    if dept_id:
                        dept_name = self.departments.get(dept_id, 'Unknown')
                        dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
        
        else:  # Internal exam
            # Internal: Two students per bench (left/right)
            # Allocations have isLeftSeat flag
            bench_map = {}  # seat_number -> {left, right}
            
            for alloc in hall_allocations:
                seat_num = alloc['seatNumber']
                is_left = alloc.get('isLeftSeat', True)
                reg_no = alloc.get('registerNumber', '-')
                
                if seat_num not in bench_map:
                    bench_map[seat_num] = {'left': '-', 'right': '-'}
                
                if is_left:
                    bench_map[seat_num]['left'] = reg_no
                else:
                    bench_map[seat_num]['right'] = reg_no
                
                # Count department
                dept_id = alloc.get('department')
                if dept_id:
                    dept_name = self.departments.get(dept_id, 'Unknown')
                    dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
            
            # Convert bench_map to 2D layout
            for seat_num, bench in bench_map.items():
                idx = seat_num - 1  # 0-indexed
                col = idx // rows_per_col
                row = idx % rows_per_col
                
                if col < num_cols and row < rows_per_col:
                    layout[row][col] = bench
        
        occupied = sum(1 for row in layout for cell in row if cell != '-')
        
        return layout, dept_counts, occupied
    
    def _generate_hall_visual(self, hall_id):
        """Generate matplotlib figure for one hall matching original format exactly"""
        hall_info = self.halls.get(hall_id, {})
        hall_allocations = self.hall_wise_allocations.get(hall_id, [])
        hall_no = hall_info.get('hallNumber', 'Unknown')
        
        num_cols = hall_info.get('numberOfColumns', 4)
        rows_per_col = hall_info.get('rowsPerColumn', 15)
        
        # Convert to 2D layout
        layout, dept_counts, occupied = self._convert_to_2d_layout(hall_allocations, hall_info)
        
        # Create figure (A4 landscape: 11.69 x 8.27 inches)
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis('off')
        
        # College header - exact positioning
        fig.text(0.5, 0.96, 'Marri Laxman Reddy Institute of Technology',
                ha='center', fontsize=16, fontweight='bold')
        fig.text(0.5, 0.93, 'Hyderabad - 43',
                ha='center', fontsize=11)
        fig.text(0.5, 0.90, '[An Autonomous Institution]',
                ha='center', fontsize=9, style='italic')
        
        # Title
        if self.exam_type == 'Internal':
            roman_numeral = 'I' if self.internal_number == 1 else 'II'
            exam_type_text = f'Continuous Internal Assessment - {roman_numeral}'
        else:
            exam_type_text = 'End Semester Examination'
        fig.text(0.5, 0.87, f'SEATING ARRANGEMENT ({exam_type_text})',
                ha='center', fontsize=14, fontweight='bold')
        
        # Date, session, hall info
        fig.text(0.1, 0.82, f'Date: {self.generation_date}', fontsize=10)
        if self.exam_type == 'Internal':
            fig.text(0.5, 0.82, f'Session: Morning', ha='center', fontsize=10)
        else:
            fig.text(0.5, 0.82, f'Session: {self.session}', ha='center', fontsize=10)
        fig.text(0.9, 0.82, f'Hall: {hall_no}', ha='right', fontsize=10)
        
        # Column headers
        col_headers = [f'Column {i+1}' for i in range(num_cols)]
        
        # Prepare table data
        if self.exam_type == 'SEM':
            # SEM: Simple grid
            table_data = [col_headers]
            for row in layout:
                table_data.append(row)
        else:
            # Internal: Split cells "Left | Right"
            table_data = [col_headers]
            for row in layout:
                row_data = []
                for cell in row:
                    if isinstance(cell, dict):
                        left = cell.get('left', '-')
                        right = cell.get('right', '-')
                        cell_text = f"{left} | {right}"
                        row_data.append(cell_text)
                    else:
                        row_data.append(str(cell))
                table_data.append(row_data)
        
        # Main seating table
        table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                        bbox=[0.1, 0.20, 0.8, 0.57])
        
        # Style table
        table.auto_set_font_size(False)
        if self.exam_type == 'Internal':
            table.set_fontsize(6)
            table.scale(1, 2.0)
        else:
            table.set_fontsize(9)
            table.scale(1, 2)
        
        # Style all cells
        for key, cell in table.get_celld().items():
            cell.set_edgecolor('black')
            cell.set_linewidth(1)
            cell.set_facecolor('white')
            
            # Bold header row
            if key[0] == 0:
                cell.set_text_props(weight='bold')
        
        # Department breakdown table at bottom
        dept_data = [[dept, count] for dept, count in dept_counts.items()]
        dept_data.insert(0, ['Department', 'Count'])
        dept_data.append(['Total Number of Students:', str(occupied)])
        
        dept_table = ax.table(cellText=dept_data, cellLoc='left', loc='lower center',
                             bbox=[0.1, 0.05, 0.5, 0.15])
        dept_table.auto_set_font_size(False)
        dept_table.set_fontsize(9)
        dept_table.scale(1, 1.5)
        
        # Style department table
        for key, cell in dept_table.get_celld().items():
            cell.set_edgecolor('black')
            cell.set_linewidth(1)
            cell.set_facecolor('white')
            if key[0] == 0 or key[0] == len(dept_data) - 1:
                cell.set_text_props(weight='bold')
        
        plt.tight_layout()
        return fig
    
    def generate_seating_pdf_student(self, output_dir='uploads/seating'):
        """Generate student PDF with hall layouts using matplotlib"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Load allocations from database if not already loaded
        if not self.hall_wise_allocations:
            allocations = list(self.db.allocations.find({'schedule': self.schedule_id}))
            if not allocations:
                return {"success": False, "message": "No allocations found for this schedule"}
            
            # Group by hall
            self.hall_wise_allocations = {}
            for alloc in allocations:
                hall_id = alloc['hall']
                if hall_id not in self.hall_wise_allocations:
                    self.hall_wise_allocations[hall_id] = []
                self.hall_wise_allocations[hall_id].append(alloc)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seating_student_{self.schedule_id}_{timestamp}.pdf"
        output_file = os.path.join(output_dir, filename)
        
        # Filter non-empty halls
        non_empty_halls = [hall_id for hall_id in sorted(self.hall_wise_allocations.keys())
                          if len(self.hall_wise_allocations[hall_id]) > 0]
        
        if not non_empty_halls:
            return {"success": False, "message": "No halls with students"}
        
        # Generate PDF using matplotlib
        with PdfPages(output_file) as pdf:
            for hall_id in non_empty_halls:
                fig = self._generate_hall_visual(hall_id)
                pdf.savefig(fig, bbox_inches='tight', facecolor='white')
                plt.close(fig)
        
        return {
            "success": True,
            "message": "Student seating PDF generated successfully",
            "pdfPath": output_file,
            "filename": filename
        }
    
    def generate_seating_pdf_faculty(self, output_dir='uploads/seating'):
        """Generate faculty PDF with summary table (portrait A4)"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Load allocations from database if not already loaded
        if not self.hall_wise_allocations:
            allocations = list(self.db.allocations.find({'schedule': self.schedule_id}))
            if not allocations:
                return {"success": False, "message": "No allocations found for this schedule"}
            
            # Group by hall
            self.hall_wise_allocations = {}
            for alloc in allocations:
                hall_id = alloc['hall']
                if hall_id not in self.hall_wise_allocations:
                    self.hall_wise_allocations[hall_id] = []
                self.hall_wise_allocations[hall_id].append(alloc)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"seating_faculty_{self.schedule_id}_{timestamp}.pdf"
        output_file = os.path.join(output_dir, filename)
        
        # Use portrait A4
        doc = SimpleDocTemplate(output_file, pagesize=A4,
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=30)
        
        elements = []
        styles = getSampleStyleSheet()
        
        # College Header styles
        header_style = ParagraphStyle(
            'CollegeHeader',
            parent=styles['Heading1'],
            fontSize=16,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        sub_header_style = ParagraphStyle(
            'SubHeader',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=4
        )
        
        italic_style = ParagraphStyle(
            'Italic',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Oblique',
            alignment=TA_CENTER,
            spaceAfter=6
        )
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=14,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        # Add header
        elements.append(Paragraph("Marri Laxman Reddy Institute of Technology", header_style))
        elements.append(Paragraph("Hyderabad - 43", sub_header_style))
        elements.append(Paragraph("[An Autonomous Institution]", italic_style))
        elements.append(Paragraph("SEATING ARRANGEMENT - FACULTY SUMMARY", title_style))
        elements.append(Paragraph(f"Date: {self.generation_date} | Session: {self.session}", sub_header_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Overall Statistics
        total_students = len(self.allocations)
        halls_used = len(self.hall_wise_allocations)
        
        stats_data = [
            ['Overall Statistics', ''],
            ['Total Students Allocated:', str(total_students)],
            ['Total Halls Used:', str(halls_used)],
            ['Exam Type:', self.exam_type],
            ['Year of Study:', f'Year {self.year}']
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(stats_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Hall Allocation Summary
        elements.append(Paragraph("Hall Allocation Summary", styles['Heading2']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Create cell style for wrapping text
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            wordWrap='CJK'
        )
        
        hall_data = [['Hall No.', 'Capacity', 'Allocated', 'Department Breakdown', 'Invigilators Needed']]
        
        for hall_id in sorted(self.hall_wise_allocations.keys()):
            hall_info = self.halls.get(hall_id, {})
            hall_allocations = self.hall_wise_allocations[hall_id]
            hall_no = hall_info.get('hallNumber', 'Unknown')
            capacity = hall_info.get('capacity', 0)
            allocated = len(hall_allocations)
            
            # Department breakdown
            dept_counts = {}
            for alloc in hall_allocations:
                dept_id = alloc.get('department')
                if dept_id:
                    dept_name = self.departments.get(dept_id, 'Unknown')
                    dept_counts[dept_name] = dept_counts.get(dept_name, 0) + 1
            
            dept_breakdown = ", ".join([f"{dept}: {count}" for dept, count in dept_counts.items()])
            invigilators = max(1, allocated // 30)
            
            # Wrap department breakdown in Paragraph for text wrapping
            dept_para = Paragraph(dept_breakdown, cell_style)
            
            hall_data.append([
                str(hall_no),
                str(capacity),
                str(allocated),
                dept_para,  # Use Paragraph object for wrapping
                str(invigilators)
            ])
        
        hall_table = Table(hall_data, colWidths=[0.6*inch, 0.7*inch, 0.7*inch, 3.4*inch, 1.8*inch])
        hall_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            ('TOPPADDING', (0, 1), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(hall_table)
        
        # Build PDF
        doc.build(elements)
        
        return {
            "success": True,
            "message": "Faculty duty roster PDF generated successfully",
            "pdfPath": output_file,
            "filename": filename
        }
    
    def allocate_seats(self):
        """Allocate seats for students (MongoDB version)"""
        # Get students for this schedule (support multiple schemas)
        # Try common field names: yearOfStudy or year; registerNumber or registerNo or regno; name or studentName
        query_variants = [
            {'yearOfStudy': self.year, 'isActive': True},
            {'year': self.year, 'isActive': True},
            {'yearOfStudy': self.year},
            {'year': self.year}
        ]
        students = []
        for q in query_variants:
            try:
                cur = self.db.students.find(q).sort([('department', 1), ('registerNumber', 1)])
                students = list(cur)
                if students:
                    break
            except Exception:
                continue
        
        if not students:
            # Gracefully succeed with no allocations to avoid backend mock fallback
            return {
                "success": True,
                "message": "No students found for allocation; skipping seat assignment",
                "allocations": [],
                "totalStudents": 0,
                "totalHalls": 0
            }
        
        # Get available halls (respect halls list from request when provided)
        halls = []
        if self.schedule_data and self.schedule_data.get('halls'):
            # Use provided hall IDs
            hall_ids = [ObjectId(h) if isinstance(h, str) else h for h in self.schedule_data['halls']]
            halls = list(self.db.halls.find({'_id': {'$in': hall_ids}, 'isActive': True}).sort('hallNumber', 1))
        else:
            halls_cursor = self.db.halls.find({'isActive': True}).sort('hallNumber', 1)
            halls = list(halls_cursor)
        
        if not halls:
            return {"success": False, "message": "No halls available"}
        
        # Allocation logic based on exam type
        allocations = []
        hall_idx = 0
        current_hall_seat = 1
        current_hall = halls[hall_idx]
        students_in_current_hall = 0
        
        for student in students:
            # Check if current hall is full
            if self.exam_type == 'SEM':
                # SEM: One student per seat
                max_students_in_hall = current_hall['capacity']
            else:  # Internal
                # Internal: Two students per bench, capacity is number of benches
                max_students_in_hall = current_hall['capacity'] * 2
            
            if students_in_current_hall >= max_students_in_hall:
                # Current hall is full, move to next hall
                hall_idx += 1
                if hall_idx >= len(halls):
                    return {"success": False, "message": "Not enough halls for all students"}
                current_hall = halls[hall_idx]
                current_hall_seat = 1
                students_in_current_hall = 0
            
            # Create allocation
            if self.exam_type == 'SEM':
                reg_no = student.get('registerNumber') or student.get('registerNo') or student.get('regno') or '-'
                name = student.get('name') or student.get('studentName') or ''
                alloc = {
                    'schedule': self.schedule_id,
                    'hall': current_hall['_id'],
                    'hallNumber': current_hall['hallNumber'],
                    'seatNumber': current_hall_seat,
                    'student': student['_id'],
                    'registerNumber': reg_no,
                    'studentName': name,
                    'department': student['department'],
                    'isLeftSeat': True,
                    'pdfGenerated': False
                }
                allocations.append(alloc)
                current_hall_seat += 1
                students_in_current_hall += 1
            
            else:  # Internal - two students per bench
                # Determine if this is left or right seat in current bench
                is_left = (students_in_current_hall % 2 == 0)
                reg_no = student.get('registerNumber') or student.get('registerNo') or student.get('regno') or '-'
                name = student.get('name') or student.get('studentName') or ''
                
                alloc = {
                    'schedule': self.schedule_id,
                    'hall': current_hall['_id'],
                    'hallNumber': current_hall['hallNumber'],
                    'seatNumber': current_hall_seat,
                    'student': student['_id'],
                    'registerNumber': reg_no,
                    'studentName': name,
                    'department': student['department'],
                    'isLeftSeat': is_left,
                    'pdfGenerated': False
                }
                allocations.append(alloc)
                students_in_current_hall += 1
                
                # Move to next bench only after filling both left AND right seats
                if not is_left:  # Just filled right side
                    current_hall_seat += 1
        
        # Delete existing allocations for this schedule first
        self.db.allocations.delete_many({'schedule': self.schedule_id})
        
        # Save to MongoDB
        if allocations:
            self.db.allocations.insert_many(allocations)
        
        # Update schedule status
        self.db.schedules.update_one(
            {'_id': self.schedule_id},
            {'$set': {'seatingAllocated': True}}
        )
        
        # Convert ObjectIds to strings for JSON serialization
        serializable_allocations = []
        for alloc in allocations:
            alloc_copy = {}
            for key, value in alloc.items():
                if isinstance(value, ObjectId):
                    alloc_copy[key] = str(value)
                elif key == '_id' and value:
                    alloc_copy[key] = str(value)
                else:
                    alloc_copy[key] = value
            serializable_allocations.append(alloc_copy)
        
        return {
            "success": True,
            "message": "Seating allocated successfully",
            "allocations": serializable_allocations,
            "totalStudents": len(allocations),
            "totalHalls": hall_idx + 1
        }

def main():
    """Command-line interface"""
    if len(sys.argv) < 3:
        print("Usage: python seating_wrapper.py <command> <schedule_id> [output_dir]")
        print("Commands: allocate_seats, generate_student_pdf, generate_faculty_pdf")
        sys.exit(1)
    
    command = sys.argv[1]
    schedule_id_param = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'uploads/seating'
    
    # Handle both JSON object and plain schedule_id
    schedule_id = schedule_id_param
    schedule_data = None
    try:
        if '{' in schedule_id_param and 'scheduleId' in schedule_id_param:
            # Parse JSON object and extract scheduleId + data
            data = json.loads(schedule_id_param)
            schedule_id = data.get('scheduleId') or data.get('_id')
            if not schedule_id:
                raise ValueError("No scheduleId found in JSON")
            # Keep the data for fallback if schedule not in DB
            schedule_data = data
    except json.JSONDecodeError as e:
        # If JSON parsing fails, assume it's a plain schedule_id
        pass
    except Exception as e:
        # Any other error, try to use as-is
        pass
    
    try:
        allocator = MongoSeatingAllocator(schedule_id, schedule_data)
        
        if command == 'allocate_seats':
            result = allocator.allocate_seats()
        elif command == 'generate_student_pdf':
            result = allocator.generate_seating_pdf_student(output_dir)
        elif command == 'generate_faculty_pdf':
            result = allocator.generate_seating_pdf_faculty(output_dir)
        else:
            result = {"success": False, "message": f"Unknown command: {command}"}
        
        print(json.dumps(result))
        sys.exit(0 if result.get('success') else 1)
    
    except Exception as e:
        print(json.dumps({"success": False, "message": str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    main()
