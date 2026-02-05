"""
Main Flask Application - Exam Management System
Integrates existing exam scheduling, seating allocation, and hall ticket modules
"""
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from functools import wraps
from bson import ObjectId
from datetime import datetime, timedelta
import os
import random
import io
import base64

# PDF generation imports - use your existing pdf_generator module
from pdf_generator import SchedulePDFGenerator, generate_schedule_pdf
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from config import get_db, SECRET_KEY, DEFAULT_PASSWORD, DEPARTMENTS, SEMESTER_MAPPING, PDF_STORAGE_PATH, BASE_DIR, SESSION_TIMINGS

app = Flask(__name__, 
            template_folder=os.path.join(BASE_DIR, 'templates'),
            static_folder=os.path.join(BASE_DIR, 'static'))
app.secret_key = SECRET_KEY


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') != role:
                return "Access Denied", 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/')
def index():
    """Home page - redirect to login"""
    if 'user_id' in session:
        return redirect(url_for(f"{session['role']}_dashboard"))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Common login page for all roles"""
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        db = get_db()
        user = db.users.find_one({"email": email})
        
        if user and user['password'] == password:
            session['user_id'] = str(user['_id'])
            session['email'] = user['email']
            session['role'] = user['role']
            session['name'] = user['name']
            
            if user['role'] == 'student':
                session['regno'] = user['regno']
                session['department'] = user['department']
                session['year'] = user['year']
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'faculty':
                session['faculty_id'] = user['faculty_id']
                session['department'] = user['department']
                return redirect(url_for('faculty_dashboard'))
            elif user['role'] == 'coe':
                return redirect(url_for('coe_dashboard'))
        else:
            error = "Invalid email or password"
    
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    return redirect(url_for('login'))


# =============== STUDENT DASHBOARD ===============
@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    """Student dashboard"""
    db = get_db()
    
    # Get student details
    student = db.users.find_one({"_id": ObjectId(session['user_id'])})
    
    # Get exam schedules for this student's year and department
    year = student['year']
    department = student['department']
    
    # Calculate current semester (assume odd semester for simplicity, COE selects actual)
    # Get active exam cycles for this student
    exam_cycles = list(db.exam_cycles.find({
        "year": year,
        "status": "scheduled"
    }).sort("created_at", -1))
    
    # Check authorization for hall ticket download
    auth = db.authorizations.find_one({"type": "global"})
    hall_ticket_enabled = auth.get('hall_ticket_enabled', False) if auth else False
    
    # Get student's exam schedules
    schedules = []
    for cycle in exam_cycles:
        cycle_schedules = list(db.exam_schedules.find({
            "exam_cycle_id": cycle['_id'],
            "department": department
        }).sort("date", 1))
        
        if cycle_schedules:
            schedules.append({
                "cycle": cycle,
                "exams": cycle_schedules
            })
    
    return render_template('student_dashboard.html', 
                         student=student,
                         schedules=schedules,
                         hall_ticket_enabled=hall_ticket_enabled)


# =============== FACULTY DASHBOARD ===============
@app.route('/faculty/dashboard')
@role_required('faculty')
def faculty_dashboard():
    """Faculty dashboard"""
    db = get_db()
    
    # Get faculty details
    faculty = db.users.find_one({"_id": ObjectId(session['user_id'])})
    faculty_id = faculty['faculty_id']
    
    # Get invigilation assignments
    assignments = list(db.seating_arrangements.find({
        "invigilator_id": faculty_id
    }))
    
    # Enrich assignments with exam cycle info
    for assignment in assignments:
        cycle = db.exam_cycles.find_one({"_id": assignment['exam_cycle_id']})
        assignment['cycle'] = cycle
    
    # Check authorization for QR scanning
    auth = db.authorizations.find_one({"type": "global"})
    qr_scan_enabled = auth.get('qr_scan_enabled', False) if auth else False
    
    return render_template('faculty_dashboard.html',
                         faculty=faculty,
                         assignments=assignments,
                         qr_scan_enabled=qr_scan_enabled)


# =============== COE DASHBOARD ===============
@app.route('/coe/dashboard')
@role_required('coe')
def coe_dashboard():
    """COE dashboard"""
    db = get_db()
    
    # Get all exam cycles
    exam_cycles = list(db.exam_cycles.find().sort("created_at", -1))
    
    # Get departments
    departments = list(db.departments.find())
    
    # Get halls
    halls = list(db.exam_halls.find())
    
    # Get faculty
    faculty = list(db.users.find({"role": "faculty"}))
    
    # Get authorization status
    auth = db.authorizations.find_one({"type": "global"})
    
    return render_template('coe_dashboard.html',
                         exam_cycles=exam_cycles,
                         departments=departments,
                         halls=halls,
                         faculty=faculty,
                         auth=auth)


@app.route('/coe/toggle_authorization', methods=['POST'])
@role_required('coe')
def toggle_authorization():
    """Toggle hall ticket or QR scan authorization"""
    db = get_db()
    auth_type = request.form.get('auth_type')
    
    auth = db.authorizations.find_one({"type": "global"})
    if auth:
        if auth_type == 'hall_ticket':
            new_value = not auth.get('hall_ticket_enabled', False)
            db.authorizations.update_one(
                {"type": "global"},
                {"$set": {"hall_ticket_enabled": new_value}}
            )
        elif auth_type == 'qr_scan':
            new_value = not auth.get('qr_scan_enabled', False)
            db.authorizations.update_one(
                {"type": "global"},
                {"$set": {"qr_scan_enabled": new_value}}
            )
    
    return redirect(url_for('coe_dashboard'))


@app.route('/coe/view_attendance/<exam_cycle_id>')
@role_required('coe')
def view_attendance(exam_cycle_id):
    """View attendance for an exam cycle"""
    db = get_db()
    
    cycle = db.exam_cycles.find_one({"_id": ObjectId(exam_cycle_id)})
    if not cycle:
        return "Exam cycle not found", 404
    
    # Get all attendance records for this cycle
    attendance_records = list(db.attendance.find({"exam_cycle_id": ObjectId(exam_cycle_id)}))
    
    # Get schedules
    schedules = list(db.exam_schedules.find({"exam_cycle_id": ObjectId(exam_cycle_id)}))
    
    # Organize attendance by schedule
    attendance_by_schedule = {}
    for schedule in schedules:
        schedule_id = str(schedule['_id'])
        present = []
        absent = []
        
        # Get students for this department
        students = list(db.users.find({
            "role": "student",
            "department": schedule['department'],
            "year": cycle['year']
        }))
        
        for student in students:
            att = db.attendance.find_one({
                "exam_cycle_id": ObjectId(exam_cycle_id),
                "schedule_id": schedule['_id'],
                "regno": student['regno']
            })
            
            if att and att.get('status') == 'present':
                present.append(student)
            else:
                absent.append(student)
        
        attendance_by_schedule[schedule_id] = {
            "schedule": schedule,
            "present": present,
            "absent": absent
        }
    
    return render_template('attendance_view.html',
                         cycle=cycle,
                         attendance_by_schedule=attendance_by_schedule)


@app.route('/api/get_student_count', methods=['GET'])
@role_required('coe')
def get_student_count():
    """Get student count for a specific year"""
    db = get_db()
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({"error": "Year is required"}), 400
    
    count = db.users.count_documents({"role": "student", "year": year})
    return jsonify({"count": count})


# ==================== EXAM SCHEDULING (COE) ====================

@app.route('/coe/create_schedule', methods=['GET', 'POST'])
@role_required('coe')
def create_schedule():
    """Create exam schedule - Combined with automatic seating allocation"""
    db = get_db()
    
    if request.method == 'POST':
        return handle_schedule_creation(db)
    
    halls = list(db.exam_halls.find())
    faculty = list(db.users.find({"role": "faculty"}))
    departments = list(db.departments.find())
    
    return render_template('create_schedule.html',
                         halls=halls,
                         faculty=faculty,
                         departments=departments,
                         current_year=datetime.now().year)


def handle_schedule_creation(db):
    """Handle schedule creation and AUTOMATIC seating allocation"""
    try:
        academic_year = request.form.get('academic_year')
        exam_type = request.form.get('exam_type')
        year = int(request.form.get('year'))
        semester_type = request.form.get('semester_type')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
        
        holidays_str = request.form.get('holidays', '')
        holidays = []
        if holidays_str:
            holidays = [datetime.strptime(d.strip(), '%Y-%m-%d') 
                       for d in holidays_str.split(',') if d.strip()]
        
        selected_faculty = request.form.getlist('faculty')
        selected_halls = request.form.getlist('halls')
        
        if not selected_faculty or not selected_halls:
            return "Please select at least one faculty and one hall", 400
        
        semester = SEMESTER_MAPPING[year]['odd' if semester_type == 'odd' else 'even']
        
        exam_cycle = {
            "academic_year": academic_year,
            "exam_type": exam_type,
            "year": year,
            "semester": semester,
            "semester_type": semester_type,
            "start_date": start_date,
            "end_date": end_date,
            "holidays": holidays,
            "selected_faculty": selected_faculty,
            "selected_halls": selected_halls,
            "status": "scheduled",
            "created_at": datetime.now(),
            "seating_pdf_paths": []
        }
        
        result = db.exam_cycles.insert_one(exam_cycle)
        exam_cycle_id = result.inserted_id
        
        subjects_by_dept = {}
        for dept in DEPARTMENTS:
            subjects = list(db.subjects.find({"semester": semester, "department": dept}))
            subjects_by_dept[dept] = subjects
        
        schedules = generate_exam_schedule(
            db, exam_cycle_id, exam_type, year, semester,
            start_date, end_date, holidays, subjects_by_dept
        )
        
        if schedules:
            db.exam_schedules.insert_many(schedules)
        
        # AUTOMATIC SEATING ALLOCATION - triggered immediately after scheduling
        seating_result = generate_seating_allocation(
            db, exam_cycle_id, exam_type, year, selected_halls, selected_faculty
        )
        
        if seating_result['success']:
            pdf_paths = generate_seating_pdfs(db, exam_cycle_id)
            db.exam_cycles.update_one(
                {"_id": exam_cycle_id},
                {"$set": {"seating_pdf_paths": pdf_paths}}
            )
        
        return redirect(url_for('coe_dashboard'))
        
    except Exception as e:
        return f"Error: {str(e)}", 500


def generate_exam_schedule(db, exam_cycle_id, exam_type, year, semester,
                          start_date, end_date, holidays, subjects_by_dept):
    """
    Generate exam schedule with constraints:
    - One exam per department per day
    - HEAVY subjects: minimum 1 full-day gap
    - NONMAJOR subjects: minimum half-day gap
    """
    schedules = []
    
    available_dates = []
    current_date = start_date
    while current_date <= end_date:
        if current_date not in holidays and current_date.weekday() != 6:
            available_dates.append(current_date)
        current_date += timedelta(days=1)
    
    if not available_dates:
        return schedules
    
    sessions = ["FN", "AN"] if exam_type == "Semester" else ["FN"]
    
    last_heavy_exam = {dept: None for dept in DEPARTMENTS}
    last_nonmajor_exam = {dept: None for dept in DEPARTMENTS}
    exams_per_day_dept = {}
    
    all_subjects = []
    for dept, subjects in subjects_by_dept.items():
        for subj in subjects:
            all_subjects.append({"subject": subj, "department": dept})
    
    all_subjects.sort(key=lambda x: (0 if x['subject']['type'] == 'HEAVY' else 1))
    
    date_idx = 0
    session_idx = 0
    
    for item in all_subjects:
        subj = item['subject']
        dept = item['department']
        scheduled = False
        attempts = 0
        temp_date_idx = date_idx
        temp_session_idx = session_idx
        
        while not scheduled and attempts < len(available_dates) * len(sessions) * 2:
            current_exam_date = available_dates[temp_date_idx]
            current_session = sessions[temp_session_idx]
            can_schedule = True
            
            day_key = (dept, current_exam_date.strftime('%Y-%m-%d'))
            if day_key in exams_per_day_dept:
                can_schedule = False
            
            if can_schedule and subj['type'] == 'HEAVY' and last_heavy_exam[dept]:
                if (current_exam_date - last_heavy_exam[dept]).days < 1:
                    can_schedule = False
            
            if can_schedule and subj['type'] == 'NONMAJOR' and last_nonmajor_exam[dept]:
                last_exam = last_nonmajor_exam[dept]
                if current_exam_date == last_exam['date']:
                    if exam_type == "Semester" and last_exam['session'] == 'FN' and current_session == 'FN':
                        can_schedule = False
                    elif exam_type != "Semester":
                        can_schedule = False
            
            if can_schedule:
                schedule = {
                    "exam_cycle_id": exam_cycle_id,
                    "subject_code": subj['code'],
                    "subject_name": subj['name'],
                    "subject_type": subj['type'],
                    "department": dept,
                    "date": current_exam_date,
                    "session": current_session,
                    "exam_type": exam_type,
                    "year": year,
                    "semester": semester
                }
                schedules.append(schedule)
                
                exams_per_day_dept[day_key] = True
                if subj['type'] == 'HEAVY':
                    last_heavy_exam[dept] = current_exam_date
                else:
                    last_nonmajor_exam[dept] = {'date': current_exam_date, 'session': current_session}
                
                scheduled = True
            
            temp_session_idx += 1
            if temp_session_idx >= len(sessions):
                temp_session_idx = 0
                temp_date_idx += 1
                if temp_date_idx >= len(available_dates):
                    temp_date_idx = 0
            attempts += 1
        
        if scheduled:
            session_idx = temp_session_idx + 1
            if session_idx >= len(sessions):
                session_idx = 0
                date_idx = temp_date_idx + 1
                if date_idx >= len(available_dates):
                    date_idx = 0
    
    return schedules


def generate_seating_allocation(db, exam_cycle_id, exam_type, year, selected_halls, selected_faculty):
    """
    Generate seating allocation AUTOMATICALLY after scheduling:
    - Semester: 1 student per bench
    - Internal: 2 students per bench (different departments)
    - Minimum 2 departments per hall
    """
    try:
        students = list(db.users.find({"role": "student", "year": year}))
        if not students:
            return {"success": False, "error": "No students"}
        
        halls = list(db.exam_halls.find({"hall_id": {"$in": selected_halls}}))
        if not halls:
            return {"success": False, "error": "No halls"}
        
        schedules = list(db.exam_schedules.find({"exam_cycle_id": exam_cycle_id}))
        if not schedules:
            return {"success": False, "error": "No schedules"}
        
        schedules_by_slot = {}
        for schedule in schedules:
            slot_key = (schedule['date'].strftime('%Y-%m-%d'), schedule['session'])
            if slot_key not in schedules_by_slot:
                schedules_by_slot[slot_key] = []
            schedules_by_slot[slot_key].append(schedule)
        
        random.seed(int(exam_cycle_id.binary.hex(), 16) % (2**32))
        faculty_availability = {fac_id: [] for fac_id in selected_faculty}
        seating_arrangements = []
        
        for slot_key, slot_schedules in schedules_by_slot.items():
            date_str, session = slot_key
            slot_departments = [s['department'] for s in slot_schedules]
            slot_students = [s for s in students if s['department'] in slot_departments]
            
            if not slot_students:
                continue
            
            random.shuffle(slot_students)
            students_per_bench = 2 if exam_type in ["Internal 1", "Internal 2"] else 1
            all_students_with_dept = [(s, s['department']) for s in slot_students]
            random.shuffle(all_students_with_dept)
            
            student_idx = 0
            available_faculty = [f for f in selected_faculty if slot_key not in faculty_availability[f]]
            
            for hall_idx, hall in enumerate(halls):
                if student_idx >= len(all_students_with_dept):
                    break
                
                hall_id = hall['hall_id']
                bench_capacity = hall['bench_capacity']
                columns = hall['columns']
                
                seating = []
                departments_in_hall = set()
                bench_num = 0
                row = 1
                col = 1
                
                while bench_num < bench_capacity and student_idx < len(all_students_with_dept):
                    bench_students = []
                    
                    for _ in range(students_per_bench):
                        if student_idx >= len(all_students_with_dept):
                            break
                        
                        student, dept = all_students_with_dept[student_idx]
                        
                        if students_per_bench == 2 and len(bench_students) == 1:
                            for temp_idx in range(student_idx, min(student_idx + 50, len(all_students_with_dept))):
                                temp_student, temp_dept = all_students_with_dept[temp_idx]
                                if temp_dept != bench_students[0]['department']:
                                    all_students_with_dept[student_idx], all_students_with_dept[temp_idx] = \
                                        all_students_with_dept[temp_idx], all_students_with_dept[student_idx]
                                    student, dept = temp_student, temp_dept
                                    break
                        
                        bench_students.append({
                            "regno": student['regno'],
                            "name": student['name'],
                            "department": dept
                        })
                        departments_in_hall.add(dept)
                        student_idx += 1
                    
                    if bench_students:
                        seating.append({
                            "bench": bench_num + 1,
                            "row": row,
                            "column": col,
                            "students": bench_students
                        })
                        bench_num += 1
                        col += 1
                        if col > columns:
                            col = 1
                            row += 1
                
                if seating:
                    if hall_idx < len(available_faculty):
                        fac_id = available_faculty[hall_idx]
                        faculty_availability[fac_id].append(slot_key)
                    else:
                        fac_id = selected_faculty[hall_idx % len(selected_faculty)]
                    
                    seating_arrangements.append({
                        "exam_cycle_id": exam_cycle_id,
                        "date": datetime.strptime(date_str, '%Y-%m-%d'),
                        "session": session,
                        "hall_id": hall_id,
                        "invigilator_id": fac_id,
                        "seating": seating,
                        "departments_present": list(departments_in_hall),
                        "student_count": sum(len(s['students']) for s in seating),
                        "created_at": datetime.now()
                    })
        
        if seating_arrangements:
            db.seating_arrangements.insert_many(seating_arrangements)
        
        return {"success": True, "count": len(seating_arrangements)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_seating_pdfs(db, exam_cycle_id):
    """Generate PDF files for seating arrangements - matching your original format"""
    cycle_pdf_dir = os.path.join(PDF_STORAGE_PATH, str(exam_cycle_id))
    os.makedirs(cycle_pdf_dir, exist_ok=True)
    
    pdf_paths = []
    arrangements = list(db.seating_arrangements.find({"exam_cycle_id": exam_cycle_id}))
    cycle = db.exam_cycles.find_one({"_id": exam_cycle_id})
    
    # Generate individual hall seating PDFs
    for arr in arrangements:
        date_str = arr['date'].strftime('%Y-%m-%d')
        session_name = arr['session']
        hall_id = arr['hall_id']
        filename = f"seating_{date_str}_{session_name}_{hall_id}.pdf"
        filepath = os.path.join(cycle_pdf_dir, filename)
        
        generate_hall_seating_pdf(filepath, arr, cycle)
        
        pdf_paths.append({"filename": filename, "date": date_str, "session": session_name, "hall_id": hall_id})
    
    # Generate Faculty Summary PDF
    faculty_filename = f"faculty_summary_{cycle['exam_type'].replace(' ', '_')}.pdf"
    faculty_filepath = os.path.join(cycle_pdf_dir, faculty_filename)
    generate_faculty_summary_pdf(faculty_filepath, arrangements, cycle)
    pdf_paths.append({"filename": faculty_filename, "date": "Summary", "session": "-", "hall_id": "ALL"})
    
    # Generate Exam Schedule PDF using your original format
    schedules = list(db.exam_schedules.find({"exam_cycle_id": exam_cycle_id}))
    schedule_filename = f"exam_schedule_{cycle['exam_type'].replace(' ', '_')}.pdf"
    schedule_filepath = os.path.join(cycle_pdf_dir, schedule_filename)
    generate_exam_schedule_pdf(schedule_filepath, schedules, cycle)
    pdf_paths.append({"filename": schedule_filename, "date": "Schedule", "session": "-", "hall_id": "-"})
    
    return pdf_paths


def generate_hall_seating_pdf(filepath, arrangement, cycle):
    """Generate PDF for seating arrangement - matching your original Seating Arrangement format"""
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    # College Header - matching your original format
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
    
    elements.append(Paragraph("Marri Laxman Reddy Institute of Technology", header_style))
    elements.append(Paragraph("Hyderabad - 43", sub_header_style))
    elements.append(Paragraph("[An Autonomous Institution]", italic_style))
    elements.append(Paragraph(f"SEATING ARRANGEMENT - {cycle['exam_type'].upper()}", title_style))
    
    date_formatted = arrangement['date'].strftime('%d-%m-%Y')
    session_time = SESSION_TIMINGS.get('FN_INTERNAL' if 'Internal' in cycle['exam_type'] else 'FN') if arrangement['session'] == 'FN' else SESSION_TIMINGS.get('AN_INTERNAL' if 'Internal' in cycle['exam_type'] else 'AN')
    elements.append(Paragraph(f"Date: {date_formatted} | Session: {arrangement['session']} ({session_time})", sub_header_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Hall Info
    departments_list = arrangement.get('departments_present', [])
    info_data = [
        ['Hall', arrangement['hall_id']],
        ['Invigilator', arrangement['invigilator_id']],
        ['Total Students', str(arrangement['student_count'])],
        ['Departments', ', '.join(map(str, departments_list))]
    ]
    
    info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Seating table
    headers = ['Seat No', 'Register Number', 'Name', 'Dept']
    data = [headers]
    
    seat_no = 1
    for seat in arrangement['seating']:
        for student in seat['students']:
            data.append([str(seat_no), student['regno'], student['name'], str(student['department'])])
            seat_no += 1
    
    col_widths = [0.6*inch, 1.8*inch, 2.8*inch, 0.8*inch]
    seating_table = Table(data, colWidths=col_widths, repeatRows=1)
    
    seating_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(seating_table)
    
    doc.build(elements)


def generate_faculty_summary_pdf(filepath, arrangements, cycle):
    """Generate Faculty Summary PDF - matching your original format"""
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=30)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # College Header
    header_style = ParagraphStyle('CollegeHeader', parent=styles['Heading1'], fontSize=16,
                                  fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=6)
    sub_header_style = ParagraphStyle('SubHeader', parent=styles['Normal'], fontSize=11,
                                      alignment=TA_CENTER, spaceAfter=4)
    italic_style = ParagraphStyle('Italic', parent=styles['Normal'], fontSize=9,
                                  fontName='Helvetica-Oblique', alignment=TA_CENTER, spaceAfter=6)
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=14,
                                 fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=12)
    
    elements.append(Paragraph("Marri Laxman Reddy Institute of Technology", header_style))
    elements.append(Paragraph("Hyderabad - 43", sub_header_style))
    elements.append(Paragraph("[An Autonomous Institution]", italic_style))
    elements.append(Paragraph("SEATING ARRANGEMENT - FACULTY SUMMARY", title_style))
    elements.append(Paragraph(f"{cycle['exam_type']} | Year {cycle['year']} | {cycle['academic_year']}", sub_header_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Overall Statistics
    total_students = sum(arr['student_count'] for arr in arrangements)
    halls_used = len(set(arr['hall_id'] for arr in arrangements))
    
    stats_data = [
        ['Overall Statistics', ''],
        ['Total Students', str(total_students)],
        ['Total Halls Used', str(halls_used)],
        ['Exam Type', cycle['exam_type']]
    ]
    
    stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
    stats_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Hall Allocation Summary Table
    summary_title = Paragraph("Hall Allocation Summary", styles['Heading2'])
    elements.append(summary_title)
    elements.append(Spacer(1, 0.2*inch))
    
    table_data = [['Hall', 'Date', 'Session', 'Students', 'Invigilator', 'Departments']]
    
    for arr in sorted(arrangements, key=lambda x: (x['date'], x['session'], x['hall_id'])):
        depts = arr.get('departments_present', [])
        dept_str = ', '.join(map(str, depts))
        table_data.append([
            arr['hall_id'],
            arr['date'].strftime('%d-%m-%Y'),
            arr['session'],
            str(arr['student_count']),
            arr['invigilator_id'],
            dept_str
        ])
    
    col_widths = [0.7*inch, 0.9*inch, 0.6*inch, 0.6*inch, 1.3*inch, 2.1*inch]
    summary_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(summary_table)
    
    doc.build(elements)


def generate_exam_schedule_pdf(filepath, schedules, cycle):
    """Generate Exam Schedule PDF - using your original SchedulePDFGenerator format"""
    # Convert schedules to the format expected by your pdf_generator
    schedule_data = []
    for s in schedules:
        schedule_data.append({
            'date': s['date'].strftime('%d.%m.%Y'),
            'session': s['session'],
            'subject_code': s['subject_code'],
            'subject_name': s['subject_name'],
            'department': s['department']
        })
    
    exam_type = 'INTERNAL' if 'Internal' in cycle['exam_type'] else 'SEMESTER'
    
    generate_schedule_pdf(
        schedule=schedule_data,
        violations=[],
        exam_type=exam_type,
        year=cycle['year'],
        start_date=cycle['start_date'],
        end_date=cycle['end_date'],
        filename=filepath
    )


@app.route('/coe/view_schedule/<exam_cycle_id>')
@role_required('coe')
def view_schedule(exam_cycle_id):
    """View exam schedule details"""
    db = get_db()
    
    cycle = db.exam_cycles.find_one({"_id": ObjectId(exam_cycle_id)})
    if not cycle:
        return "Exam cycle not found", 404
    
    schedules = list(db.exam_schedules.find({
        "exam_cycle_id": ObjectId(exam_cycle_id)
    }).sort([("date", 1), ("session", 1)]))
    
    seating = list(db.seating_arrangements.find({"exam_cycle_id": ObjectId(exam_cycle_id)}))
    
    return render_template('view_schedule.html', cycle=cycle, schedules=schedules, seating=seating)


@app.route('/coe/download_seating/<exam_cycle_id>/<filename>')
@role_required('coe')
def download_seating(exam_cycle_id, filename):
    """Download seating arrangement PDF file"""
    filepath = os.path.join(PDF_STORAGE_PATH, exam_cycle_id, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='application/pdf', as_attachment=False)
    return "File not found", 404


# ==================== HALL TICKET GENERATION ====================

@app.route('/hallticket/generate/<exam_cycle_id>')
@role_required('student')
def generate_hall_ticket(exam_cycle_id):
    """Generate hall ticket - only for Semester exams when authorized"""
    db = get_db()
    
    auth = db.authorizations.find_one({"type": "global"})
    if not auth or not auth.get('hall_ticket_enabled', False):
        return "Hall ticket download not authorized yet", 403
    
    cycle = db.exam_cycles.find_one({"_id": ObjectId(exam_cycle_id)})
    if not cycle:
        return "Exam cycle not found", 404
    
    if cycle['exam_type'] != 'Semester':
        return "Hall tickets only for Semester exams", 403
    
    student = db.users.find_one({"_id": ObjectId(session['user_id'])})
    if student['year'] != cycle['year']:
        return "No exams in this cycle", 403
    
    schedules = list(db.exam_schedules.find({
        "exam_cycle_id": ObjectId(exam_cycle_id),
        "department": student['department']
    }).sort("date", 1))
    
    if not schedules:
        return "No exams found", 404
    
    seating_info = get_student_seating_info(db, exam_cycle_id, student['regno'])
    qr_image = generate_qr_code(f"/verify/{exam_cycle_id}/{student['regno']}")
    
    return render_template('hall_ticket.html',
                         student=student,
                         cycle=cycle,
                         schedules=schedules,
                         seating_info=seating_info,
                         qr_image=qr_image)


def get_student_seating_info(db, exam_cycle_id, regno):
    """Get seating info for a student"""
    arrangements = list(db.seating_arrangements.find({"exam_cycle_id": ObjectId(exam_cycle_id)}))
    seating_info = {}
    for arr in arrangements:
        for seat in arr['seating']:
            for student in seat['students']:
                if student['regno'] == regno:
                    key = f"{arr['date'].strftime('%Y-%m-%d')}_{arr['session']}"
                    seating_info[key] = {
                        "hall_id": arr['hall_id'],
                        "bench": seat['bench'],
                        "row": seat['row'],
                        "column": seat['column']
                    }
    return seating_info


def generate_qr_code(data):
    """Generate QR code as base64"""
    try:
        import qrcode
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
    except:
        return ""


# ==================== QR VERIFICATION & ATTENDANCE ====================

@app.route('/verify/<exam_cycle_id>/<regno>')
def verify_student(exam_cycle_id, regno):
    """QR verification - marks attendance"""
    db = get_db()
    
    auth = db.authorizations.find_one({"type": "global"})
    if not auth or not auth.get('qr_scan_enabled', False):
        return render_template('verify_result.html', success=False, error="QR scanning not authorized")
    
    cycle = db.exam_cycles.find_one({"_id": ObjectId(exam_cycle_id)})
    if not cycle:
        return render_template('verify_result.html', success=False, error="Exam cycle not found")
    
    student = db.users.find_one({"regno": regno.upper()})
    if not student:
        return render_template('verify_result.html', success=False, error="Student not found")
    
    now = datetime.now()
    today = now.date()
    
    schedules = list(db.exam_schedules.find({
        "exam_cycle_id": ObjectId(exam_cycle_id),
        "department": student['department'],
        "date": {
            "$gte": datetime.combine(today, datetime.min.time()),
            "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())
        }
    }))
    
    if not schedules:
        return render_template('verify_result.html', success=False, error="No exam today")
    
    current_exam = None
    for schedule in schedules:
        exam_start = datetime.strptime("09:30" if schedule['session'] == 'FN' else "14:00", "%H:%M").time()
        window_start = (datetime.combine(today, exam_start) - timedelta(minutes=30)).time()
        window_end = (datetime.combine(today, exam_start) + timedelta(minutes=30)).time()
        
        if window_start <= now.time() <= window_end:
            current_exam = schedule
            break
    
    if not current_exam:
        return render_template('verify_result.html', success=False, error="Outside scan window (30 min before/after)")
    
    seating = None
    arr = db.seating_arrangements.find_one({
        "exam_cycle_id": ObjectId(exam_cycle_id),
        "session": current_exam['session'],
        "date": {"$gte": datetime.combine(today, datetime.min.time()), "$lt": datetime.combine(today + timedelta(days=1), datetime.min.time())}
    })
    if arr:
        for seat in arr['seating']:
            for s in seat['students']:
                if s['regno'].upper() == regno.upper():
                    seating = {"hall_id": arr['hall_id'], "bench": seat['bench']}
    
    db.attendance.update_one(
        {"exam_cycle_id": ObjectId(exam_cycle_id), "schedule_id": current_exam['_id'], "regno": regno.upper()},
        {"$set": {"status": "present", "marked_at": now, "subject_code": current_exam['subject_code']}},
        upsert=True
    )
    
    return render_template('verify_result.html', success=True, student=student, exam=current_exam, seating=seating, marked_at=now)


@app.route('/faculty/qr_scan')
@role_required('faculty')
def qr_scan_page():
    """QR scanning page for faculty"""
    db = get_db()
    auth = db.authorizations.find_one({"type": "global"})
    qr_enabled = auth.get('qr_scan_enabled', False) if auth else False
    
    assignments = list(db.seating_arrangements.find({"invigilator_id": session.get('faculty_id')}))
    return render_template('qr_scan.html', enabled=qr_enabled, assignments=assignments)


@app.route('/faculty/attendance/<exam_cycle_id>')
@role_required('faculty')
def faculty_attendance(exam_cycle_id):
    """View attendance"""
    db = get_db()
    cycle = db.exam_cycles.find_one({"_id": ObjectId(exam_cycle_id)})
    attendance = list(db.attendance.find({"exam_cycle_id": ObjectId(exam_cycle_id)}))
    return render_template('attendance_list.html', cycle=cycle, attendance=attendance)


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('seating_pdfs', exist_ok=True)
    os.makedirs('hall_tickets', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, port=5000)
