#!/usr/bin/env python3
"""
Hall Ticket Generation Wrapper with MongoDB Integration
Generates hall tickets for students based on exam schedules
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient
import qrcode
from io import BytesIO
import base64

# Import ReportLab for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class MongoHallTicketGenerator:
    """Generates hall tickets from MongoDB data"""
    
    def __init__(self, schedule_id=None):
        """Initialize generator with MongoDB connection"""
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['exam_management']
        self.schedules = self.db['schedules']
        self.students = self.db['students']
        self.subjects = self.db['subjects']
        self.schedule_id = ObjectId(schedule_id) if schedule_id else None
        self.schedule_data = None
        
    def load_schedule_data(self):
        """Load schedule information from MongoDB"""
        if not self.schedule_id:
            raise ValueError("Schedule ID is required")
            
        # Get schedule document
        schedule = self.schedules.find_one({'_id': self.schedule_id})
        if not schedule:
            raise ValueError(f"Schedule not found: {self.schedule_id}")
            
        self.schedule_data = schedule
        return schedule
        
    def generate_qr_base64(self, data):
        """Generate QR code as base64 image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return img_base64
        
    def fetch_student_data(self, register_number):
        """Fetch student information from MongoDB"""
        # Try different field name variants
        student = self.students.find_one({
            '$or': [
                {'registerNumber': register_number},
                {'registerNo': register_number},
                {'regno': register_number},
                {'reg_no': register_number}
            ]
        })
        
        if not student:
            raise ValueError(f"Student not found: {register_number}")
            
        return student
        
    def fetch_subjects_for_student(self, student):
        """Fetch exam subjects for the student based on schedule"""
        if not self.schedule_data:
            self.load_schedule_data()
            
        # Get subjects from the timetable in schedule
        timetable = self.schedule_data.get('timetable', [])
        
        # Filter subjects based on student's year/semester
        student_year = student.get('yearOfStudy') or student.get('year')
        student_semester = student.get('semester') or student.get('sem')
        
        subjects_list = []
        for entry in timetable:
            # Check if subject matches student's year/semester
            subject_year = entry.get('year')
            subject_semester = entry.get('semester')
            
            if subject_year == student_year or not subject_year:
                # Get subject details
                subject_code = entry.get('subjectCode', '')
                subject_name = entry.get('subjectName', '')
                exam_date = entry.get('date', '')
                session = entry.get('session', '')
                
                # Format date if it's a datetime object
                if isinstance(exam_date, datetime):
                    exam_date = exam_date.strftime('%d.%m.%Y')
                elif isinstance(exam_date, str) and exam_date:
                    try:
                        # Try to parse and reformat
                        dt = datetime.strptime(exam_date, '%Y-%m-%d')
                        exam_date = dt.strftime('%d.%m.%Y')
                    except:
                        pass
                
                subjects_list.append({
                    'sem': str(student_semester) if student_semester else '',
                    'date': exam_date,
                    'session': session,
                    'code': subject_code,
                    'name': subject_name
                })
        
        return subjects_list
        
    def create_hall_ticket_pdf(self, student_data, subjects, qr_image):
        """Create hall ticket PDF using ReportLab"""
        
        # Get student fields with fallbacks
        name = student_data.get('name') or student_data.get('studentName', '')
        reg_no = (student_data.get('registerNumber') or 
                 student_data.get('registerNo') or 
                 student_data.get('regno') or 
                 student_data.get('reg_no', ''))
        
        deg = student_data.get('degree', 'B.Tech')
        branch = student_data.get('branch', '')
        dob = student_data.get('dateOfBirth', '')
        if isinstance(dob, datetime):
            dob = dob.strftime('%d.%m.%Y')
            
        sem = str(student_data.get('semester') or student_data.get('sem', ''))
        gender = student_data.get('gender', '')
        regulation = student_data.get('regulation', '')
        
        # Get exam session from schedule
        exam_type = self.schedule_data.get('examType', 'SEM')
        academic_year = self.schedule_data.get('academicYear', '')
        semester_name = self.schedule_data.get('semester', '')
        
        # Format semtime (e.g., "END SEMESTER EXAMINATION – APR 2025")
        semtime = f"{semester_name} {academic_year}".strip()
        
        # Create styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.black,
            spaceAfter=2*mm,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=2*mm,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        small_center_style = ParagraphStyle(
            'SmallCenter',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=2*mm,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=2*mm,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        exam_style = ParagraphStyle(
            'ExamStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=4*mm,
            alignment=TA_CENTER
        )
        
        # Build story
        story = []
        
        # Header
        story.append(Paragraph("MARRI LAXMAN REDDY INSTITUTE OF TECHNOLOGY", title_style))
        story.append(Paragraph("HYDERABAD – 43", subtitle_style))
        story.append(Paragraph("[An Autonomous Institution]", small_center_style))
        story.append(Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATION", heading_style))
        story.append(Paragraph("HALL TICKET", heading_style))
        story.append(Paragraph(semtime, exam_style))
        
        # Add QR code (top right)
        story.append(Spacer(1, 5*mm))
        if qr_image:
            qr_img = Image(qr_image, width=35*mm, height=35*mm)
            story.append(qr_img)
            story.append(Spacer(1, 5*mm))
        
        # Student information table
        info_data = [
            [Paragraph('<b>Name:</b> ' + name, styles['Normal']), 
             Paragraph('<b>Register Number:</b> ' + reg_no, styles['Normal'])],
            [Paragraph('<b>Degree & Branch:</b> ' + deg + ' AND ' + branch, styles['Normal']), ''],
            [Paragraph('<b>Date of Birth:</b> ' + dob, styles['Normal']), 
             Paragraph('<b>Semester:</b> ' + sem, styles['Normal'])],
            [Paragraph('<b>Gender:</b> ' + gender, styles['Normal']), 
             Paragraph('<b>Regulation:</b> ' + regulation, styles['Normal'])]
        ]
        
        info_table = Table(info_data, colWidths=[95*mm, 95*mm])
        info_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
            ('SPAN', (0, 1), (1, 1)),  # Merge degree & branch row
        ]))
        
        story.append(info_table)
        story.append(Spacer(1, 5*mm))
        
        # Subjects table
        subjects_data = [['Sem', 'Date', 'Session', 'Subject Code', 'Subject Name']]
        
        for subject in subjects:
            subjects_data.append([
                subject['sem'],
                subject['date'],
                subject['session'],
                subject['code'],
                subject['name']
            ])
        
        subjects_table = Table(
            subjects_data,
            colWidths=[19*mm, 28.5*mm, 22.8*mm, 34.2*mm, 85.5*mm]
        )
        
        subjects_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Sem column
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Session column
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 2*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2*mm),
            ('TOPPADDING', (0, 0), (-1, -1), 2*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2*mm),
        ]))
        
        story.append(subjects_table)
        
        return story
        
    def generate_hall_ticket_pdf(self, register_number, output_path=None):
        """Generate hall ticket PDF for a student"""
        
        # Load schedule data
        if not self.schedule_data:
            self.load_schedule_data()
            
        # Fetch student data
        student_data = self.fetch_student_data(register_number)
        
        # Fetch subjects
        subjects = self.fetch_subjects_for_student(student_data)
        
        # Generate QR code image
        qr_data = f"http://localhost:5000/verify/{register_number}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save QR code to BytesIO
        qr_buffer = BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Default output path if not provided
        if not output_path:
            output_dir = Path(__file__).parent.parent / 'outputs' / 'hall_tickets'
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f'hall_ticket_{register_number}.pdf'
        
        # Create PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=15*mm,
            rightMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        # Build content
        story = self.create_hall_ticket_pdf(student_data, subjects, qr_buffer)
        
        # Generate PDF
        doc.build(story)
        
        return str(output_path)
        
    def generate_bulk_hall_tickets(self, year=None, output_dir=None):
        """Generate hall tickets for all students in a year"""
        
        if not self.schedule_data:
            self.load_schedule_data()
            
        # Query students
        query = {}
        if year:
            query = {'$or': [
                {'yearOfStudy': year},
                {'year': year}
            ]}
            
        students_list = list(self.students.find(query))
        
        if not students_list:
            return {
                'success': True,
                'message': 'No students found',
                'generated': []
            }
            
        # Default output directory
        if not output_dir:
            output_dir = Path(__file__).parent.parent / 'outputs' / 'hall_tickets'
            output_dir.mkdir(parents=True, exist_ok=True)
            
        generated = []
        errors = []
        
        for student in students_list:
            try:
                reg_no = (student.get('registerNumber') or 
                         student.get('registerNo') or 
                         student.get('regno') or 
                         student.get('reg_no'))
                
                if not reg_no:
                    errors.append({'student': str(student.get('_id')), 'error': 'No register number'})
                    continue
                    
                pdf_path = self.generate_hall_ticket_pdf(
                    reg_no, 
                    output_path=Path(output_dir) / f'hall_ticket_{reg_no}.pdf'
                )
                
                generated.append({
                    'registerNumber': reg_no,
                    'name': student.get('name') or student.get('studentName'),
                    'pdfPath': pdf_path
                })
                
            except Exception as e:
                errors.append({
                    'student': str(student.get('_id')),
                    'error': str(e)
                })
                
        return {
            'success': True,
            'generated': generated,
            'errors': errors,
            'total': len(students_list),
            'successful': len(generated),
            'failed': len(errors)
        }
        
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()


def main():
    """CLI interface for backend integration"""
    if len(sys.argv) < 3:
        print(json.dumps({
            'success': False,
            'error': 'Usage: hall_ticket_wrapper.py <schedule_id> <command> [args]'
        }))
        return 1
        
    schedule_id = sys.argv[1]
    command = sys.argv[2]
    
    generator = None
    
    try:
        generator = MongoHallTicketGenerator(schedule_id)
        
        if command == 'generate_single':
            # Generate single hall ticket
            if len(sys.argv) < 4:
                raise ValueError("Register number required for generate_single")
                
            register_number = sys.argv[3]
            pdf_path = generator.generate_hall_ticket_pdf(register_number)
            
            result = {
                'success': True,
                'pdfPath': pdf_path,
                'registerNumber': register_number
            }
            
        elif command == 'generate_bulk':
            # Generate bulk hall tickets
            year = int(sys.argv[3]) if len(sys.argv) > 3 else None
            result = generator.generate_bulk_hall_tickets(year)
            
        else:
            result = {
                'success': False,
                'error': f'Unknown command: {command}'
            }
            
        print(json.dumps(result))
        return 0
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }))
        return 1
        
    finally:
        if generator:
            generator.close()


if __name__ == '__main__':
    sys.exit(main())
