import qrcode
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from db import students_col, schedules_col, users_col, db
import os

class HallTicketManager:
    def __init__(self):
        pass
        
    def generate_qr(self, data):
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer

    def generate_ticket_pdf(self, reg_no, output_path):
        # 1. Fetch Student
        student = students_col.find_one({'register_number': reg_no})
        if not student:
            return False
            
        # 2. Fetch Exams for Student's Year/Sem (and check if they are scheduled)
        # Assuming hall tickets are only for "SEMESTER" exams or all scheduled exams?
        # Typically Hall tickets for End Sem.
        # Let's fetch all exams for this students year/sem that are scheduled.
        
        exams = list(schedules_col.find({
            'year': student['year'],
            'semester': student['semester']
        }).sort('date', 1))
        
        if not exams:
             # No exams scheduled, cannot generate ticket
             return False

        # 3. Generate PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Header
        elements.append(Paragraph("Marri Laxman Reddy Institute of Technology", styles['Title']))
        elements.append(Paragraph("HALL TICKET - Academic Year 2024-25", styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        # Student Details & Photo (Placeholder) & QR
        # Layout: Table with 2 columns
        
        # QR Code
        # Link to verify route
        # In real world, use actual domain. For mock, localhost is fine or just the reg_no string.
        # Requirement: "The scan must automatically mark the student as present in MongoDB."
        # The QR should contain enough info for the scanner (Faculty Dashboard) to identify the student.
        # Usually it's just the Register Number.
        
        qr_data = f"{reg_no}"
        qr_img_buffer = self.generate_qr(qr_data)
        qr_img = Image(qr_img_buffer, width=100, height=100)
        
        student_info = [
            [Paragraph(f"<b>Name:</b> {student['name']}", styles['Normal'])],
            [Paragraph(f"<b>Register No:</b> {student['register_number']}", styles['Normal'])],
            [Paragraph(f"<b>Branch:</b> {student['department']}", styles['Normal'])],
            [Paragraph(f"<b>Year/Sem:</b> {student['year']} / {student['semester']}", styles['Normal'])]
        ]
        
        info_table = Table(student_info)
        
        main_layout = Table([[info_table, qr_img]], colWidths=[300, 150])
        main_layout.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT')
        ]))
        
        elements.append(main_layout)
        elements.append(Spacer(1, 20))
        
        # Exam Table
        table_data = [['Date', 'Session', 'Subject Code', 'Subject Name']]
        for exam in exams:
            table_data.append([
                exam['date'],
                exam['session'],
                exam['subject_code'],
                exam['subject_name']
            ])
            
        exam_table = Table(table_data, colWidths=[80, 60, 80, 250])
        exam_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6)
        ]))
        
        elements.append(exam_table)
        elements.append(Spacer(1, 40))
        
        elements.append(Paragraph("Controller of Examinations", styles['Normal']))
        
        doc.build(elements)
        return True

    def toggle_release(self, is_released: bool):
        # Store in settings collection
        db['settings'].update_one(
            {'key': 'hall_ticket_release'}, 
            {'$set': {'value': is_released}}, 
            upsert=True
        )

    def is_released(self):
        setting = db['settings'].find_one({'key': 'hall_ticket_release'})
        return setting['value'] if setting else False
