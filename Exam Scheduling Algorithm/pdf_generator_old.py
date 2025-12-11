"""
PDF Generation Module for Exam Schedules
Generates formatted PDF timetables matching institutional format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import config

class SchedulePDFGenerator:
    def __init__(self, filename='exam_schedule.pdf'):
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=portrait(A4),
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Custom styles matching institutional format
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        self.highlight_style = ParagraphStyle(
            'Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            backColor=colors.yellow
        )
        
        self.branch_style = ParagraphStyle(
            'Branch',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
    
    def add_institutional_header(self, exam_type, year, start_date, end_date):
        """Add institutional header matching reference format"""
        # Main institution title
        title = Paragraph(
            "SRI SHAKTHI INSTITUTE OF ENGINEERING AND TECHNOLOGY",
            self.title_style
        )
        self.elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(
            "(An Autonomous Institution)",
            self.subtitle_style
        )
        self.elements.append(subtitle)
        
        # Office details
        office = Paragraph(
            "Office of the Controller of Examinations",
            self.subtitle_style
        )
        self.elements.append(office)
        
        self.elements.append(Spacer(1, 8))
        
        # Reference number and date
        ref_date = datetime.now().strftime('%d/%m/%Y')
        ref_info = Paragraph(
            f'<para align="left">Lr. No. 1604: SIET/COE/2025-26 ODD</para><para align="right">Date: {ref_date}</para>',
            self.subtitle_style
        )
        self.elements.append(ref_info)
        
        self.elements.append(Spacer(1, 6))
        
        # Time table title
        if exam_type == 'SEMESTER':
            tt_title = Paragraph(
                f"TIME TABLE - B.E./B.Tech. DEGREE EXAMINATIONS - Year {year}",
                self.title_style
            )
            self.elements.append(tt_title)
            
            # Regulations
            regulations = Paragraph(
                "(Regulations 2021)",
                self.highlight_style
            )
            self.elements.append(regulations)
            
            # Exam timing
            timing = Paragraph(
                "EXAM TIMING: FN : 9.30AM to 12.30PM & AN : 1.30PM to 4.30PM",
                self.highlight_style
            )
            self.elements.append(timing)
        else:
            # Internal exams
            tt_title = Paragraph(
                f"Continuous Internal Assessment - Year {year}",
                self.title_style
            )
            self.elements.append(tt_title)
            
            # Timing
            timing = Paragraph(
                "EXAM TIMING: 8:30 AM to 10:00 AM",
                self.highlight_style
            )
            self.elements.append(timing)
        
        self.elements.append(Spacer(1, 10))
    
    def add_department_schedule_semester(self, dept_schedule, dept_name):
        """Add semester exam schedule table for one department"""
        # Branch name header
        branch_header = Paragraph(f"<b>Branch Name:</b> {dept_name}", self.branch_style)
        self.elements.append(branch_header)
        self.elements.append(Spacer(1, 6))
        
        # Prepare table data
        if exam_type == 'SEMESTER':
            headers = ['Date', 'Session', 'Time', 'Dept', 'Code', 'Subject Name', 'Type']
        else:
            headers = ['Date', 'Time', 'Dept', 'Code', 'Subject Name', 'Type']
        
        data = [headers]
        
        # Group by date
        schedule_by_date = {}
        for item in schedule:
            date = item['date']
            if date not in schedule_by_date:
                schedule_by_date[date] = []
            schedule_by_date[date].append(item)
        
        # Build table rows
        for date in sorted(schedule_by_date.keys(), key=lambda x: datetime.strptime(x, '%d.%m.%Y')):
            exams = schedule_by_date[date]
            
            # Sort by session then department
            session_order = {'FN': 0, 'AN': 1, 'SINGLE': 0}
            exams.sort(key=lambda x: (session_order.get(x['session'], 2), x['department']))
            
            for i, exam in enumerate(exams):
                date_str = date if i == 0 else ''
                
                if exam_type == 'SEMESTER':
                    time_str = config.SESSION_TIMINGS.get(exam['session'], '')
                    row = [
                        date_str,
                        exam['session'],
                        time_str,
                        exam['department'],
                        exam['subject_code'],
                        exam['subject_name'],
                        exam['subject_type']
                    ]
                else:
                    time_str = config.SESSION_TIMINGS.get('SINGLE', '')
                    row = [
                        date_str,
                        time_str,
                        exam['department'],
                        exam['subject_code'],
                        exam['subject_name'],
                        exam['subject_type']
                    ]
                
                data.append(row)
        
        # Create table
        if exam_type == 'SEMESTER':
            col_widths = [1*inch, 0.7*inch, 1.3*inch, 0.7*inch, 0.8*inch, 2.5*inch, 0.9*inch]
        else:
            col_widths = [1*inch, 1.3*inch, 0.7*inch, 0.8*inch, 2.8*inch, 0.9*inch]
        
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (3, -1), 'CENTER'),
            ('ALIGN', (4, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#2c5282')),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ])
        
        table.setStyle(table_style)
        self.elements.append(table)
    
    def add_violations_table(self, violations):
        """Add violations table"""
        if not violations:
            self.elements.append(Spacer(1, 20))
            no_violations = Paragraph(
                "✅ <b>No Constraint Violations - Perfect Schedule!</b>",
                self.normal_style
            )
            self.elements.append(no_violations)
            return
        
        self.elements.append(PageBreak())
        
        violations_heading = Paragraph("CONSTRAINT VIOLATIONS", self.heading_style)
        self.elements.append(violations_heading)
        
        warning = Paragraph(
            f"<i>⚠️ {len(violations)} constraint violation(s) detected. "
            "These occur due to insufficient time slots or tight scheduling requirements.</i>",
            self.normal_style
        )
        self.elements.append(warning)
        self.elements.append(Spacer(1, 10))
        
        # Prepare violations table
        headers = ['Subject Code', 'Severity', 'Issue Description']
        data = [headers]
        
        for v in violations:
            row = [
                v['subject_code'],
                v['severity'],
                v['description']
            ]
            data.append(row)
        
        table = Table(data, colWidths=[1.2*inch, 1*inch, 5*inch], repeatRows=1)
        
        # Style violations table
        table_style = TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c53030')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#c53030')),
            
            # Highlight severity
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff5f5')]),
        ])
        
        table.setStyle(table_style)
        self.elements.append(table)
    
    def add_department_summary(self, dept_summary):
        """Add department-wise summary"""
        self.elements.append(Spacer(1, 20))
        
        dept_heading = Paragraph("DEPARTMENT-WISE SUMMARY", self.heading_style)
        self.elements.append(dept_heading)
        
        # Prepare summary table
        headers = ['Department', 'Total Exams', 'Heavy Subjects', 'Non-Major Subjects']
        data = [headers]
        
        for dept in sorted(dept_summary.keys()):
            counts = dept_summary[dept]
            row = [
                dept,
                str(counts['total']),
                str(counts.get('HEAVY', 0)),
                str(counts.get('NONMAJOR', 0))
            ]
            data.append(row)
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.8*inch])
        
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
        ])
        
        table.setStyle(table_style)
        self.elements.append(table)
    
    def generate(self):
        """Generate the PDF"""
        self.doc.build(self.elements)
        return self.filename


def generate_schedule_pdf(schedule, violations, exam_type, year, 
                          start_date, end_date, filename=None):
    """
    Generate PDF for exam schedule
    
    Args:
        schedule: List of scheduled exams
        violations: List of constraint violations
        exam_type: 'SEMESTER' or 'INTERNAL'
        year: Year group
        start_date: Start date
        end_date: End date
        filename: Output filename (optional)
    
    Returns:
        Path to generated PDF
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"exam_schedule_{exam_type.lower()}_year{year}_{timestamp}.pdf"
    
    # Calculate department summary
    dept_summary = {}
    for exam in schedule:
        dept = exam['department']
        if dept not in dept_summary:
            dept_summary[dept] = {'total': 0, 'HEAVY': 0, 'NONMAJOR': 0}
        dept_summary[dept]['total'] += 1
        dept_summary[dept][exam['subject_type']] += 1
    
    # Create PDF generator
    pdf_gen = SchedulePDFGenerator(filename)
    
    # Add sections
    pdf_gen.add_title(exam_type, year, start_date, end_date)
    pdf_gen.add_summary(len(schedule), len(violations), dept_summary)
    pdf_gen.add_schedule_table(schedule, exam_type)
    pdf_gen.add_violations_table(violations)
    pdf_gen.add_department_summary(dept_summary)
    
    # Generate PDF
    pdf_path = pdf_gen.generate()
    
    return pdf_path
