"""
PDF Generation Module for Exam Schedules
Generates formatted PDF timetables matching institutional format
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, portrait, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import config

class SchedulePDFGenerator:
    def __init__(self, filename='exam_schedule.pdf', orientation='portrait'):
        self.filename = filename
        page_size = landscape(A4) if orientation == 'landscape' else portrait(A4)
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=page_size,
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=30
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        
        # Custom styles matching institutional format
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        self.highlight_style = ParagraphStyle(
            'Highlight',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=2,
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
            spaceBefore=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        )
    
    def add_institutional_header(self, exam_type, year, start_date, end_date):
        """Add institutional header matching reference format"""
        # Main institution title
        title = Paragraph(
            "MARRI LAXMAN REDDY INSTITUTE OF TECHNOLOGY",
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
        
        self.elements.append(Spacer(1, 10))
        
        # Reference number and date (side by side)
        ref_date = datetime.now().strftime('%d/%m/%Y')
        ref_table = Table(
            [[f"Lr. No. 1604: MLRIT/COE/2025-26", f"Date: {ref_date}"]],
            colWidths=[4*inch, 2*inch]
        )
        ref_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        self.elements.append(ref_table)
        
        self.elements.append(Spacer(1, 8))
        
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
        dept_elements = []
        
        # Branch name header
        branch_header = Paragraph(f"<b>Branch Name: {dept_name}</b>", self.branch_style)
        dept_elements.append(branch_header)
        
        # Prepare table data
        headers = ['Exam Date', 'Session', 'Subject Code', 'Subject Name']
        data = [headers]
        
        # Sort by date
        dept_schedule_sorted = sorted(dept_schedule, 
                                     key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'))
        
        for exam in dept_schedule_sorted:
            row = [
                exam['date'],
                exam['session'],
                exam['subject_code'],
                exam['subject_name']
            ]
            data.append(row)
        
        # Create table
        col_widths = [1*inch, 0.8*inch, 1.1*inch, 3.1*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 1), (-1, -1), 5),
            ('RIGHTPADDING', (0, 1), (-1, -1), 5),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        table.setStyle(table_style)
        dept_elements.append(table)
        dept_elements.append(Spacer(1, 15))
        
        # Return wrapped in KeepTogether to keep department table on same page
        return KeepTogether(dept_elements)
    
    def add_department_schedule_internal(self, dept_schedule, dept_name):
        """Add internal exam schedule table for one department"""
        dept_elements = []
        
        # Branch name header
        branch_header = Paragraph(f"<b>Branch: {dept_name}</b>", self.branch_style)
        dept_elements.append(branch_header)
        
        # Prepare table data
        headers = ['Date', 'Subject Code', 'Subject Name']
        data = [headers]
        
        # Sort by date
        dept_schedule_sorted = sorted(dept_schedule, 
                                     key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'))
        
        for exam in dept_schedule_sorted:
            row = [
                exam['date'],
                exam['subject_code'],
                exam['subject_name']
            ]
            data.append(row)
        
        # Create table
        col_widths = [1*inch, 1.2*inch, 3.8*inch]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (1, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('LEFTPADDING', (0, 1), (-1, -1), 5),
            ('RIGHTPADDING', (0, 1), (-1, -1), 5),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ])
        
        table.setStyle(table_style)
        dept_elements.append(table)
        dept_elements.append(Spacer(1, 15))
        
        # Return wrapped in KeepTogether to keep department table on same page
        return KeepTogether(dept_elements)
    
    def add_internal_schedule_matrix(self, schedule):
        """Add internal exam schedule in matrix format (departments × dates)"""
        # Extract all unique dates and departments
        dates = sorted(list(set(exam['date'] for exam in schedule)), 
                      key=lambda x: datetime.strptime(x, '%d.%m.%Y'))
        departments = sorted(list(set(exam['department'] for exam in schedule)))
        
        # Create a mapping for quick lookup
        schedule_map = {}
        for exam in schedule:
            key = (exam['department'], exam['date'])
            schedule_map[key] = exam['subject_name']
        
        # Create paragraph style for wrapping text in cells
        # Uses proper word wrapping - entire words move to next line
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            wordWrap='LTR',  # Left-to-right word wrapping (breaks at word boundaries)
            splitLongWords=0  # Don't split long words across lines
        )
        
        # Build table data
        # Header row with dates (formatted with day below)
        header_row = ['Branch\n/ Date']
        for date_str in dates:
            date_obj = datetime.strptime(date_str, '%d.%m.%Y')
            day_name = date_obj.strftime('%A')
            formatted = f"{date_str}\n{day_name}"
            header_row.append(formatted)
        
        data = [header_row]
        
        # Add rows for each department
        for dept in departments:
            row = [dept]
            for date_str in dates:
                subject = schedule_map.get((dept, date_str), '')
                if subject:
                    # Wrap subject in Paragraph for automatic text wrapping
                    subject_para = Paragraph(subject, cell_style)
                    row.append(subject_para)
                else:
                    row.append('')
            data.append(row)
        
        # Calculate column widths dynamically
        num_dates = len(dates)
        # First column for branch names
        first_col_width = 0.9 * inch
        # Remaining width divided among date columns
        remaining_width = 10 * inch  # Landscape A4 minus margins
        date_col_width = remaining_width / num_dates
        
        col_widths = [first_col_width] + [date_col_width] * num_dates
        
        # Create table
        table = Table(data, colWidths=col_widths, repeatRows=1)
        
        # Style the table
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # First column (department names) styling
            ('BACKGROUND', (0, 1), (0, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (0, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('VALIGN', (0, 1), (0, -1), 'MIDDLE'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (0, -1), 10),
            
            # Body cells styling
            ('BACKGROUND', (1, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (1, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (1, 1), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (1, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (1, 1), (-1, -1), 9),
            ('TOPPADDING', (1, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (1, 1), (-1, -1), 6),
            ('LEFTPADDING', (1, 1), (-1, -1), 4),
            ('RIGHTPADDING', (1, 1), (-1, -1), 4),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
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
    Generate PDF for exam schedule in institutional format
    
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
    
    # Different layout for INTERNAL vs SEMESTER exams
    if exam_type == 'INTERNAL':
        # Use landscape orientation for internal exams (matrix format)
        pdf_gen = SchedulePDFGenerator(filename, orientation='landscape')
        
        # Add institutional header
        pdf_gen.add_institutional_header(exam_type, year, start_date, end_date)
        
        # Add internal schedule in matrix format (departments × dates)
        pdf_gen.add_internal_schedule_matrix(schedule)
        
    else:
        # Use portrait orientation for semester exams (department-wise tables)
        pdf_gen = SchedulePDFGenerator(filename, orientation='portrait')
        
        # Group schedule by department
        dept_schedules = {}
        for exam in schedule:
            dept = exam['department']
            if dept not in dept_schedules:
                dept_schedules[dept] = []
            dept_schedules[dept].append(exam)
        
        # Add institutional header
        pdf_gen.add_institutional_header(exam_type, year, start_date, end_date)
        
        # Add department-wise schedules
        for dept in sorted(dept_schedules.keys()):
            dept_table = pdf_gen.add_department_schedule_semester(dept_schedules[dept], dept)
            pdf_gen.elements.append(dept_table)
    
    # Add violations summary if any (on last page)
    if violations:
        pdf_gen.elements.append(Spacer(1, 20))
        
        violations_para = Paragraph(
            f"<b>Note:</b> {len(violations)} constraint violation(s) detected due to scheduling constraints.",
            pdf_gen.subtitle_style
        )
        pdf_gen.elements.append(violations_para)
    
    # Generate PDF
    pdf_path = pdf_gen.generate()
    
    return pdf_path
