import os
import socket
import sqlite3
import io
import base64
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
from jinja2 import Environment, FileSystemLoader
import qrcode
import pdfkit

app = Flask(__name__)
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')
# Use integrated database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'Exam Scheduling Algorithm', 'exam_scheduling.db')

# Configure wkhtmltopdf path (update if installed elsewhere)
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
try:
    PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except Exception:
    PDFKIT_CONFIG = None

env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


def get_local_ip():
    """Get local IP address for QR code URLs"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def fetch_student_and_subjects(reg_no):
    """Fetch student details and subjects from integrated database (including arrears)"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Fetch student info including arrears array
    cur.execute('''
        SELECT reg_no, name, degree, branch_full, dob, semester, gender, regulation, year, department, arrears
        FROM students WHERE reg_no=?
    ''', (reg_no,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return None
    
    # Parse arrears JSON array
    import json
    arrears_list = json.loads(row[10]) if row[10] else []
    
    # Calculate semester time (e.g., "DEC 2025" based on semester)
    semester_num = row[5]
    year_num = row[8]
    # For even semesters, typically Apr-May exams, for odd semesters, Nov-Dec exams
    if semester_num % 2 == 0:
        semtime = "APR 2026"
    else:
        semtime = "DEC 2025"
    
    student = {
        'reg_no': row[0],
        'name': row[1],
        'deg': row[2] if row[2] else 'B.Tech',
        'branch': row[3] if row[3] else row[9],  # Use branch_full or department
        'dob': row[4] if row[4] else '01.01.2000',
        'sem': str(row[5]),
        'gender': row[6] if row[6] else 'N/A',
        'semtime': semtime,
        'regulation': row[7] if row[7] else '2021',
        'year': row[8],
        'department': row[9],
        'arrears': arrears_list  # List of arrear subject codes
    }
    
    # Fetch subjects with schedule dates (current semester + arrears only)
    # Current semester: subjects student is enrolled in from their current semester
    # Arrears: subjects from arrears list that have been scheduled
    
    # Determine current semester type (ODD or EVEN)
    current_semester_type = 'EVEN' if semester_num % 2 == 0 else 'ODD'
    
    # Get student_id first
    cur.execute('SELECT student_id FROM students WHERE reg_no = ?', (reg_no,))
    student_id = cur.fetchone()[0]
    
    cur.execute('''
        SELECT 
            sub.subject_code,
            sub.subject_name,
            sub.year as subject_year,
            sub.semester_type,
            sch.exam_date,
            sch.session
        FROM subjects sub
        JOIN schedules sch ON sub.subject_id = sch.subject_id
        WHERE (
            -- Current semester subjects (enrolled + matching current semester)
            (sub.subject_id IN (
                SELECT subject_id FROM student_subjects WHERE student_id = ?
            ) AND sub.semester_type = ?)
            OR
            -- Arrear subjects (from arrears list)
            sub.subject_code IN ({})
        )
        ORDER BY sch.exam_date, sub.subject_code
    '''.format(','.join(['?' for _ in arrears_list])), 
    (student_id, current_semester_type, *arrears_list))
    
    subjects = []
    for r in cur.fetchall():
        subject_code = r[0]
        # Check if this subject is in the arrears list
        is_arrear = subject_code in arrears_list
        status = 'ARREAR' if is_arrear else 'REGULAR'
        
        subjects.append({
            'sem': str(r[2]) if r[2] else student['sem'],  # subject year
            'date': r[4] if r[4] else 'TBA',  # exam_date
            'session': r[5] if r[5] else 'TBA',  # session
            'code': subject_code,  # subject_code
            'name': r[1],  # subject_name
            'status': status  # REGULAR or ARREAR (from arrears array)
        })
    
    conn.close()
    return student, subjects


def generate_qr_base64(url):
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode()


def generate_hall_ticket_pdf(reg_no):
    """Generate hall ticket PDF using WeasyPrint"""
    # Fetch data
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return None
    
    student, subjects = data
    
    # Generate QR code pointing to verification page
    ip = get_local_ip()
    verify_url = f"http://{ip}:5000/verify/{reg_no}"
    qr_base64 = generate_qr_base64(verify_url)
    
    # Prepare context for template
    context = {
        'name': student['name'],
        'reg_no': student['reg_no'],
        'deg': student['deg'],
        'branch': student['branch'],
        'dob': student['dob'],
        'sem': student['sem'],
        'gender': student['gender'],
        'semtime': student['semtime'],
        'regulation': student.get('regulation', '2015'),
        'subjects': subjects,
        'qr_base64': qr_base64
    }
    
    # Render HTML template
    template = env.get_template('hall_ticket_template.html')
    html_content = template.render(context)
    
    # Convert HTML to PDF using pdfkit
    if PDFKIT_CONFIG is None:
        raise RuntimeError('wkhtmltopdf not found. Please install from: https://wkhtmltopdf.org/downloads.html')
    
    pdf_bytes = pdfkit.from_string(html_content, False, configuration=PDFKIT_CONFIG, options={
        'enable-local-file-access': None,
        'quiet': ''
    })
    
    return io.BytesIO(pdf_bytes)


@app.route('/')
def index():
    """Landing page with register number input form"""
    return render_template('index.html')


@app.route('/qr')
def show_qr():
    """Display QR code page for a specific register number"""
    reg_no = request.args.get('reg_no')
    if not reg_no:
        return redirect(url_for('index'))
    
    # Verify student exists
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return f"<h2>Student with Register Number '{reg_no}' not found!</h2><br><a href='/'>Go Back</a>", 404
    
    student, _ = data
    
    # Generate QR code for download link
    ip = get_local_ip()
    download_url = f"http://{ip}:5000/download/{reg_no}"
    qr_base64 = generate_qr_base64(download_url)
    
    return render_template('qr_page.html', 
                         reg_no=reg_no,
                         name=student['name'],
                         qr_base64=qr_base64,
                         download_url=download_url)


@app.route('/download/<reg_no>')
def download_hall_ticket(reg_no):
    """Generate and stream PDF hall ticket"""
    try:
        pdf_buffer = generate_hall_ticket_pdf(reg_no)
        if pdf_buffer is None:
            return f"<h2>Student with Register Number '{reg_no}' not found!</h2>", 404
        
        pdf_buffer.seek(0)
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'{reg_no}_hall_ticket.pdf'
        )
    except Exception as e:
        return f"<h2>Error generating hall ticket: {str(e)}</h2><br><a href='/'>Go Back</a>", 500


@app.route('/verify/<reg_no>')
def verify_student(reg_no):
    """Mock verification website (scanned from QR code)"""
    data = fetch_student_and_subjects(reg_no)
    if data is None:
        return f"<h2>Invalid Hall Ticket</h2><p>Register Number '{reg_no}' not found in database.</p>", 404
    
    student, subjects = data
    
    return render_template('verify.html',
                         reg_no=student['reg_no'],
                         name=student['name'],
                         branch=student['branch'],
                         degree=student['deg'],
                         semester=student['sem'])


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print("=" * 60)
        print("ERROR: Database not found!")
        print(f"Expected location: {DB_PATH}")
        print(f"Please ensure exam_scheduling.db exists in the Exam Scheduling Algorithm folder")
        print("=" * 60)
    else:
        ip = get_local_ip()
        print("=" * 60)
        print(f"Hall Ticket Generation System")
        print(f"Server running at: http://{ip}:5000")
        print(f"Local access: http://localhost:5000")
        print("=" * 60)
        app.run(host='0.0.0.0', port=5000, debug=True)
