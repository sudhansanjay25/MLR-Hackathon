"""
Scheduler Wrapper for MongoDB Integration
Connects to MongoDB, generates timetable, and creates PDF
"""
import sys
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import os

class MongoScheduler:
    def __init__(self, mongo_uri='mongodb://localhost:27017/exam_management'):
        """Initialize MongoDB connection"""
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_default_database()
        
    def generate_available_dates(self, start_date, end_date, holidays):
        """Generate list of available dates excluding weekends and holidays"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        holiday_dates = [datetime.strptime(h, '%Y-%m-%d') for h in holidays]
        
        available_dates = []
        current = start
        
        while current <= end:
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() not in [5, 6]:
                # Skip holidays
                if current not in holiday_dates:
                    available_dates.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
        
        return available_dates
    
    def get_subjects_for_year(self, year, semester, exam_type):
        """Fetch subjects from MongoDB for given year and semester"""
        subjects = list(self.db.subjects.find({
            'year': year,
            'semester': semester,
            'isActive': True
        }).sort('code', 1))
        
        return subjects
    
    def generate_timetable(self, params):
        """Generate exam timetable for ALL departments"""
        year = params['year']
        semester = params.get('semester', 1)  # Default to semester 1 if not provided
        exam_type = params['examType']
        session = params['session']
        start_date = params['startDate']
        end_date = params['endDate']
        holidays = params.get('holidays', [])
        schedule_id = params['scheduleId']
        
        # Get available dates
        available_dates = self.generate_available_dates(start_date, end_date, holidays)
        
        # Get all subjects for the year and semester, grouped by department
        subjects = self.get_subjects_for_year(year, semester, exam_type)
        
        if len(subjects) == 0:
            return {
                'success': False,
                'message': 'No subjects found for the given year',
                'timetable': []
            }
        
        # Group subjects by department
        subjects_by_dept = {}
        for subject in subjects:
            dept_id = subject.get('department')
            if dept_id:
                dept = self.db.departments.find_one({'_id': dept_id})
                if dept:
                    dept_code = dept['code']
                    if dept_code not in subjects_by_dept:
                        subjects_by_dept[dept_code] = []
                    subjects_by_dept[dept_code].append(subject)
        
        # Generate timetable entries for each department
        timetable = []
        date_idx = 0
        
        # For each date, schedule exams for all departments
        for date in available_dates:
            exams_on_date = []
            
            # For SEM exams: FN and AN sessions
            if exam_type == 'SEM':
                # FN Session - schedule one subject per department if available
                for dept_code in sorted(subjects_by_dept.keys()):
                    dept_subjects = subjects_by_dept[dept_code]
                    # Find next unscheduled subject for this dept
                    scheduled_codes = set(t['subjectCode'] for t in timetable if t.get('department') == dept_code)
                    for subject in dept_subjects:
                        if subject['code'] not in scheduled_codes:
                            exams_on_date.append({
                                'schedule': ObjectId(schedule_id),
                                'subject': subject['_id'],
                                'subjectCode': subject['code'],
                                'subjectName': subject['name'],
                                'department': dept_code,
                                'date': date,
                                'timeStart': '09:30 AM',
                                'timeEnd': '12:30 PM',
                                'session': 'FN'
                            })
                            scheduled_codes.add(subject['code'])
                            break
                
                # AN Session - schedule another subject per department if available
                for dept_code in sorted(subjects_by_dept.keys()):
                    dept_subjects = subjects_by_dept[dept_code]
                    scheduled_codes = set(t['subjectCode'] for t in timetable + exams_on_date if t.get('department') == dept_code)
                    for subject in dept_subjects:
                        if subject['code'] not in scheduled_codes:
                            exams_on_date.append({
                                'schedule': ObjectId(schedule_id),
                                'subject': subject['_id'],
                                'subjectCode': subject['code'],
                                'subjectName': subject['name'],
                                'department': dept_code,
                                'date': date,
                                'timeStart': '02:00 PM',
                                'timeEnd': '05:00 PM',
                                'session': 'AN'
                            })
                            scheduled_codes.add(subject['code'])
                            break
            
            else:  # Internal exam - single session per day
                # Schedule one subject per department
                for dept_code in sorted(subjects_by_dept.keys()):
                    dept_subjects = subjects_by_dept[dept_code]
                    scheduled_codes = set(t['subjectCode'] for t in timetable if t.get('department') == dept_code)
                    for subject in dept_subjects:
                        if subject['code'] not in scheduled_codes:
                            exams_on_date.append({
                                'schedule': ObjectId(schedule_id),
                                'subject': subject['_id'],
                                'subjectCode': subject['code'],
                                'subjectName': subject['name'],
                                'department': dept_code,
                                'date': date,
                                'timeStart': '09:30 AM',
                                'timeEnd': '12:30 PM',
                                'session': 'SINGLE'
                            })
                            scheduled_codes.add(subject['code'])
                            break
            
            # Add exams for this date to timetable
            timetable.extend(exams_on_date)
            
            # Check if all subjects scheduled
            total_scheduled = len(set(t['subjectCode'] for t in timetable))
            if total_scheduled >= len(subjects):
                break
        
        return {
            'success': True,
            'message': f'Timetable generated successfully for {len(subjects_by_dept)} departments',
            'timetable': timetable
        }
    
    def generate_timetable_pdf(self, schedule_id, output_dir='uploads/timetables'):
        """Generate PDF for exam timetable"""
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch schedule details
        schedule = self.db.examschedules.find_one({'_id': ObjectId(schedule_id)})
        if not schedule:
            return {'success': False, 'message': 'Schedule not found'}
        
        # Fetch timetable entries
        timetable_entries = list(self.db.examtimetables.find({
            'schedule': ObjectId(schedule_id)
        }).sort('date', 1))
        
        if len(timetable_entries) == 0:
            return {'success': False, 'message': 'No timetable entries found'}
        
        # Fetch subjects for each entry
        for entry in timetable_entries:
            subject = self.db.subjects.find_one({'_id': entry['subject']})
            if subject:
                entry['subjectDetails'] = subject
        
        # Generate PDF
        filename = f"timetable_{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=landscape(A4),
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=30
        )
        
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=13,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'SubTitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.black,
            spaceAfter=2,
            alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Institutional header
        title = Paragraph("MARRI LAXMAN REDDY INSTITUTE OF TECHNOLOGY", title_style)
        elements.append(title)
        
        subtitle = Paragraph("(An Autonomous Institution)", subtitle_style)
        elements.append(subtitle)
        
        office = Paragraph("Office of the Controller of Examinations", subtitle_style)
        elements.append(office)
        
        elements.append(Spacer(1, 10))
        
        # Reference number and date
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
        elements.append(ref_table)
        elements.append(Spacer(1, 8))
        
        # Timetable title
        exam_type = schedule.get('examType', 'N/A')
        year = schedule.get('year', 'N/A')
        
        if exam_type == 'SEM':
            tt_title = Paragraph(f"TIME TABLE - B.E./B.Tech. DEGREE EXAMINATIONS - Year {year}", title_style)
            elements.append(tt_title)
            regulations = Paragraph("(Regulations 2021)", subtitle_style)
            elements.append(regulations)
            timing = Paragraph("EXAM TIMING: FN : 9.30AM to 12.30PM & AN : 1.30PM to 4.30PM", subtitle_style)
            elements.append(timing)
        else:
            tt_title = Paragraph(f"Continuous Internal Assessment - Year {year}", title_style)
            elements.append(tt_title)
            timing = Paragraph("EXAM TIMING: 9:30 AM to 12:30 PM", subtitle_style)
            elements.append(timing)
        
        elements.append(Spacer(1, 15))
        
        # Timetable table
        table_data = [['Date', 'Subject Code', 'Subject Name', 'Time']]
        
        for entry in timetable_entries:
            # Handle both string and datetime objects
            if isinstance(entry['date'], str):
                date_str = datetime.strptime(entry['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
            else:
                date_str = entry['date'].strftime('%d/%m/%Y')
            
            time_str = f"{entry['timeStart']} - {entry['timeEnd']}"
            
            table_data.append([
                date_str,
                entry['subjectCode'],
                entry['subjectName'],
                time_str
            ])
        
        table = Table(table_data, colWidths=[1.5*inch, 1.5*inch, 4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return {
            'success': True,
            'message': 'PDF generated successfully',
            'pdfPath': filepath,
            'filename': filename
        }
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()

def main():
    """Main entry point for command-line execution"""
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'message': 'Usage: python scheduler_wrapper.py <command> <params_json>'
        }))
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        # Initialize scheduler
        mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/exam_management')
        scheduler = MongoScheduler(mongo_uri)
        
        if command == 'generate_timetable':
            params = json.loads(sys.argv[2])
            result = scheduler.generate_timetable(params)
            print(json.dumps(result, default=str))
            
        elif command == 'generate_pdf':
            schedule_id = sys.argv[2]
            output_dir = sys.argv[3] if len(sys.argv) > 3 else 'uploads/timetables'
            result = scheduler.generate_timetable_pdf(schedule_id, output_dir)
            print(json.dumps(result, default=str))
            
        else:
            print(json.dumps({
                'success': False,
                'message': f'Unknown command: {command}'
            }))
            sys.exit(1)
        
        scheduler.close()
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'message': str(e),
            'error': type(e).__name__
        }))
        sys.exit(1)

if __name__ == '__main__':
    main()
