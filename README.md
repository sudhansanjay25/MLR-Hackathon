# One-Stop Exam Management System

A comprehensive exam management system for educational institutions with three integrated modules: **Exam Scheduling**, **Seating Allocation**, and **Hall Ticket Generation**.

---

## 📚 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Module 1: Exam Scheduling Algorithm](#module-1-exam-scheduling-algorithm)
- [Module 2: Seating Allocation System](#module-2-seating-allocation-system)
- [Module 3: Hall Ticket Generation](#module-3-hall-ticket-generation)
- [Database Integration](#database-integration)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)

---

## Overview

This system automates the entire exam management workflow from schedule creation to hall ticket generation, ensuring:
- **Zero conflicts** in exam scheduling
- **Fair and randomized** student seating
- **Department mixing** to prevent cheating
- **Optimized resource utilization** (halls, teachers)
- **Automated PDF generation** for all documents

---

## System Architecture

```
exam_scheduling.db (SQLite)
         ↓
┌────────────────────────────────────────────────┐
│   Module 1: Exam Scheduling Algorithm         │
│   - Creates exam timetables (SEM & Internal)   │
│   - Handles constraints & violations           │
│   - Stores schedules in database               │
└────────────────┬───────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────┐
│   Module 2: Seating Allocation System         │
│   - Reads existing schedules from database     │
│   - Slot-based allocation (date + session)     │
│   - Allocates students to halls                │
│   - Assigns invigilators                       │
│   - Generates seating PDFs                     │
└────────────────┬───────────────────────────────┘
                 ↓
┌────────────────────────────────────────────────┐
│   Module 3: Hall Ticket Generation             │
│   - Creates individual hall tickets            │
│   - Shows current semester + arrears only      │
│   - Generates QR codes for verification        │
│   - Outputs printable PDFs                     │
└────────────────────────────────────────────────┘
```

---

## Module 1: Exam Scheduling Algorithm

### Location
- **Main File**: `Exam Scheduling Algorithm/scheduler.py`
- **CLI Interface**: `Exam Scheduling Algorithm/main.py`
- **Configuration**: `Exam Scheduling Algorithm/config.py`

### Why This Algorithm?

The exam scheduling problem is a **constraint satisfaction problem (CSP)** where we need to:
1. Schedule multiple subjects across multiple days and sessions
2. Avoid conflicts (same department, same day)
3. Distribute workload evenly
4. Respect holidays and weekends
5. Allow COE authority to override constraints when necessary

### How It Works

#### 1. Date Generation Algorithm

**Where**: [`scheduler.py:21-52`](Exam Scheduling Algorithm/scheduler.py#L21-L52)

```python
def generate_available_dates(start_date, end_date, holidays):
    # Excludes only Sunday (weekday 6)
    # Includes Monday-Saturday as working days
```

**Why**: 
- Provides flexibility by treating Saturday as a working day
- Automatically excludes holidays
- Ensures sufficient slots for exam scheduling

**How**:
1. Parse start and end dates
2. Iterate through each day in range
3. Check if day is Sunday (weekday 6) → skip
4. Check if day is in holidays list → skip
5. Add remaining days to available dates list

**Algorithm Complexity**: O(n) where n = number of days in range

---

#### 2. SEM Exam Scheduling Algorithm (Semester Exams)

**Where**: [`scheduler.py:159-330`](Exam Scheduling Algorithm/scheduler.py#L159-L330)

**Why**:
- Students need adequate study time between exams
- Should spread across all available days
- Each department has different numbers of subjects (5-7 subjects)
- Need to minimize consecutive exams for students

**How**:

```python
# Step 1: Group subjects by department
dept_subject_count = {}
for subject in subjects:
    dept = subject['department']
    dept_subject_count[dept].append(subject)

# Step 2: Find department with maximum subjects
max_subjects_dept = max(dept_subject_count.keys(), 
                        key=lambda d: len(dept_subject_count[d]))
subjects_to_schedule = len(dept_subject_count[max_subjects_dept])

# Step 3: Distribute across available dates
# One subject per department per day (spread strategy)
slot_index = 0
for each department:
    for each subject in department:
        assign to slots[slot_index]
        slot_index += 1
```

**Algorithm Details**:

1. **Department Parallel Scheduling**: All departments take their nth subject on the same slot
   - CSE Subject 1, ECE Subject 1, MECH Subject 1 → Same day, different sessions
   - This allows departments to progress in parallel

2. **Slot Distribution**:
   - Priority: Spread across days first, then use multiple sessions
   - Each day has 2 sessions: FN (Forenoon) and AN (Afternoon)
   - Distributes subjects to maximize days used

3. **Constraint Checking**:
   - Same department cannot have exams in consecutive slots
   - Minimum 1-day gap between consecutive exams (when possible)
   - Violations are logged but can be overridden by COE

**Complexity**: O(d × s) where d = departments, s = subjects per department

---

#### 3. Internal Exam Scheduling Algorithm

**Where**: [`scheduler.py:332-460`](Exam Scheduling Algorithm/scheduler.py#L332-L460)

**Why**:
- Internal exams are shorter (continuous assessment)
- Can be scheduled more compactly
- Need dual sessions (FN + AN) to accommodate all subjects
- Same database integration as SEM exams

**How**:

```python
# Internal exams use COMPACT scheduling
# All departments scheduled in parallel per slot
slot_index = 0
subjects_scheduled_per_dept = {dept: 0 for dept in dept_subject_count.keys()}

while any department has unscheduled subjects:
    for each department with remaining subjects:
        assign next subject to slots[slot_index]
    slot_index += 1  # Move to next slot

# Save to database (same as SEM)
for each scheduled exam:
    INSERT INTO schedules (cycle_id, subject_id, exam_date, session)
    VALUES (?, ?, ?, ?)
```

**Key Features**:
- **Database storage**: Creates exam cycle and stores schedules in database
- **Compact packing**: Fills slots sequentially without spreading
- **Dual sessions**: Uses both FN and AN on same day
- **Faster scheduling**: Completes in minimum days possible
- **Slot-based allocation**: Seating allocation reads these schedules and allocates per date/session slot

**Complexity**: O(s × d) where s = max subjects per dept, d = number of departments

---

#### 4. Constraint Validation Algorithm

**Where**: [`scheduler.py:100-150`](Exam Scheduling Algorithm/scheduler.py#L100-L150)

**Why**:
- Ensures schedule quality
- Detects conflicts early
- Provides warnings to COE for decision-making

**How**:

```python
violations = []

# Check 1: Same day constraint
for each subject:
    for each other_subject:
        if same_department and same_date:
            violations.append({
                'type': 'SAME_DAY_CONFLICT',
                'severity': 'HIGH'
            })

# Check 2: Consecutive exam constraint  
for each subject:
    if has_exam_on_consecutive_day:
        violations.append({
            'type': 'CONSECUTIVE_EXAM',
            'severity': 'MEDIUM'
        })
```

**Violation Severity Levels**:
- **HIGH**: Same department, same day → Must avoid
- **MEDIUM**: Consecutive day exams → Should avoid
- **LOW**: Short gap between exams → Nice to avoid

---

#### 5. Date Validation Algorithm

**Where**: [`main.py:328-383`](Exam Scheduling Algorithm/main.py#L328-L383)

**Why**: Prevent invalid scheduling parameters

**How**:

```python
# Validation 1: Past date check
if start_date < today:
    reject()

# Validation 2: Same start and end date
if start_date == end_date:
    reject()

# Validation 3: Duration check
if (end_date - start_date) > 365 days:
    reject()

# Validation 4: Future limit check
if end_date > today + 1 year:
    reject()
```

**Complexity**: O(1) - constant time validation

---

## Module 2: Seating Allocation System

### Location
- **Main File**: `Exam Scheduling Algorithm/seating_allocation.py`
- **Database Integration**: Reads from `exam_scheduling.db`

### Why This Algorithm?

The seating allocation problem requires:
1. **Schedule-based allocation**: Reads existing schedules from database (created by main.py)
2. **Slot-based processing**: Allocates students per date/session, not entire cycle at once
3. **Anti-cheating measures**: Students from same department shouldn't sit together
4. **Fairness**: Random distribution to prevent bias
5. **Capacity optimization**: Efficient hall usage
6. **Department diversity**: Minimum 2 departments per hall

### Workflow

**For Internal Exams:**84-180`(Exam Scheduling Algorithm/seating_allocation.py#L84-L180)

**Why**: Reads existing schedules from database, ensures consistency across all modules

**How**:

```python
def _load_from_database():
    # Load halls
    halls = cursor.execute('''
        SELECT hall_name, capacity, columns 
        FROM halls WHERE active=1
    ''')
    
    # For SEMESTER exams (with arrears)
    if exam_type == 'SEMESTER' and exam_date:
        students = cursor.execute('''
            SELECT DISTINCT s.reg_no, s.name, s.department
            FROM students s
            JOIN student_subjects ss ON s.student_id = ss.student_id
            JOIN schedules sch ON ss.subject_id = sch.subject_id
            WHERE sch.exam_date = ? AND sch.session = ? AND s.active = 1
        ''', (exam_date, session))
    
    # For INTERNAL exams (no arrears, session-based)
    elif exam_type == 'Internal' and exam_date:
        students = cursor.execute('''
            SELECT DISTINCT s.reg_no, s.name, s.department
            FROM students s
            JOIN student_subjects ss ON s.student_id = ss.student_id
            JOIN schedules sch ON ss.subject_id = sch.subject_id
            WHERE sch.session = ? AND s.year = ? AND s.active = 1
        ''', (session, year))
    
    # Load teachers
    teachers = cursor.execute('''
        SELECT teacher_name FROM teachers WHERE active=1
    ''')
```

**Key Features**:
- **Slot-based filtering**: Only loads students with exams in selected slot
- **Arrear handling**: SEM exams include students with arrears for scheduled subjects
- **No arrears for Internal**: Internal exams only consider enrolled students
    
    # Load students with new register format: {YY}MLID{DD}{NNN}
    students = cursor.execute('''
        SELECT reg_no, name, department, year 
        FROM students WHERE year=?
    ''')
    
    # Load available teachers
    teachers = cursor.execute('''
        SELECT teacher_name FROM teachers WHERE active=1
    ''')
```

**Register Number Format**:
- Format: `{YY}MLID{DD}{NNN}`
- Example: `25MLID05001` = Joined 2025, CSE (05), Student 001
- Department codes: 01=CIVIL, 02=ECE, 03=MECH, 04=EEE, 05=CSE

---

#### 2. SEM Seating Algorithm (1 student per bench)

**Where**: [`seating_allocation.py:173-252`](Seating Arangement/seating_allocation.py#L173-L252)

**Why**:
- Semester exams need maximum anti-cheating measures
- 1 student per bench = no collaboration possible
- Randomization prevents pattern prediction

**How**:

```python
def _allocate_sem_linear_optimized():
    # Step 1: Group by department and shuffle
    for dept in departments:
        dept_students = students[department == dept]
        dept_students = shuffle(dept_students, random_state=42)
        dept_groups[dept] = dept_students
    
    # Step 2: Create department pointers
    dept_pointers = {dept: 0 for dept in departments}
    
    # Step 3: Allocate with controlled randomness
    while total_allocated < total_students:
        # Ensure min 2 departments in current hall
        if len(current_hall_depts) < 2:
            select_unused_dept()
        else:
            select_random_dept()
        
        # Allocate one student
        student = dept_groups[dept][dept_pointers[dept]]
        allocate_to_seat(student, current_seat)
        
        # Move to next hall if full
        if current_seat > hall_capacity:
            move_to_next_hall()
```

**Key Features**:
1. **Controlled Randomization**: Seed=42 for reproducibility
2. **Department Diversity**: Forces minimum 2 departments per hall
3. **Sequential Filling**: Fills halls in order
4. **Pointer Tracking**: Each department has independent pointer

**Algorithm Complexity**: O(n) where n = total students

---

#### 3. Internal Seating Algorithm (2 students per bench)

**Where**: [`seating_allocation.py:258-356`](Seating Arangement/seating_allocation.py#L258-L356)

**Why**:
- Internal exams allow 2 students per bench (resource optimization)
- Bench-mates MUST be from different departments
- Maintains anti-cheating while optimizing space

**How**:

```python
def _allocate_internal_alternating_optimized():
    # Step 1: Group and shuffle by department
    dept_groups = {dept: shuffle(students[dept]) for dept in departments}
    
    # Step 2: Allocate in pairs
    while total_allocated < total_students:
        # Select first student (prefer unused department in hall)
        if len(current_hall_depts) < 2:
            dept1 = select_from_unused_depts()
        else:
            dept1 = random_choice(available_depts)
        
        student1 = dept_groups[dept1][pointer]
        allocate_to_seat(student1, current_seat)
        
        # Select second student (MUST be different department)
        other_depts = [d for d in available_depts if d != dept1]
        if other_depts:
            dept2 = random_choice(other_depts)
            student2 = dept_groups[dept2][pointer]
            allocate_to_same_seat(student2, current_seat)  # Bench-mate
        
        current_seat += 1  # Move to next bench
```

**Bench-Mate Selection Strategy**:
1. **Priority 1**: Select from different department
2. **Priority 2**: Ensure hall has minimum 2 departments
3. **Priority 3**: Random selection for fairness

**PDF Display Format**: `regno1 | regno2` (horizontal layout)

**Complexity**: O(n) where n = total students

---

#### 4. Hall Optimization Algorithm

**Where**: [`seating_allocation.py:1233-1315`](Seating Arangement/seating_allocation.py#L1233-L1315)

**Why**: 
- Minimize wasted capacity
- Reduce number of halls needed
- Optimize teacher allocation

**How**:

```python
def auto_select_halls():
    # Try multiple strategies and pick best
    
    # Strategy 1: Largest halls first (better packing)
    halls_sorted_desc = sort_by_capacity(descending=True)
    selection1 = greedy_select(halls_sorted_desc)
    
    # Strategy 2: Smallest halls first (minimize waste)
    halls_sorted_asc = sort_by_capacity(ascending=True)
    selection2 = greedy_select(halls_sorted_asc)
    
    # Compare results
    best = min(selection1, selection2, key=lambda x: (
        len(x),  # Minimize number of halls
        waste(x)  # Minimize wasted capacity
    ))
    
    # Optimization: Try removing halls
    for hall in best:
        if (total_capacity - hall_capacity) >= students_needed:
            best.remove(hall)
    
    return best
```

**Selection Criteria**:
1. **Primary**: Minimize number of halls
2. **Secondary**: Minimize wasted seats (capacity - students)
3. **Tertiary**: Prefer even distribution

**Complexity**: O(h log h + h²) where h = number of halls

---

#### 5. Department Mixing Verification

**Where**: Throughout allocation functions

**Why**: Core anti-cheating measure

**How**:

```python
# Verification during allocation
current_hall_depts = set()

for each student allocated:
    current_hall_depts.add(student.department)

# Check after hall completion
if len(current_hall_depts) < 2:
    log_warning("Hall has only 1 department")
    
# Print statistics
print(f"Hall {hall_no}: {len(current_hall_depts)} departments")
print(f"Departments: {current_hall_depts}")
```

**Minimum Requirement**: Each hall MUST have students from at least 2 different departments

---

## Module 3: Hall Ticket Generation

### Location
- **Server**: `Hall Ticket Generation/v2_weasyprint/server.py`
- **Template**: `Hall Ticket Generation/v2_weasyprint/templates/hall_ticket_template.html`

### Why This System?

Hall tickets need:
1. **Unique identification**: QR codes for verification
2. **Professional format**: Institutional branding
3. **Complete information**: Student, exam, hall details
4. **Discipline guidelines**: Examination rules

### How It Works

#### 1. QR Code Generation Algorithm

**Where**: [`server.py:75-95`](Hall Ticket Generation/v2_weasyprint/server.py#L75-L95)

**Why**: 
- Fast verification at exam halls
- Prevent fake hall tickets
- Store student data securely

**How**:

```python
def generate_qr_code(student_data):
    # Create data string
    qr_data = f"{regno}|{name}|{dept}|{year}|{exam_type}"
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,  # Size: 21x21 cells
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% error tolerance
        box_size=10,
        border=4
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for HTML embedding
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"
```

**QR Code Contents**:88-114`](Hall Ticket Generation/v2_weasyprint/server.py#L88-L114)

**Why**: Fetch student data and scheduled subjects with proper filtering

**How**:

```python
def get_student_hall_ticket_data(register_no):
    # Query 1: Get student info with arrears
    student = db.execute('''
        SELECT reg_no, name, department, year, semester,
               dob, gender, arrears
        FROM students WHERE reg_no = ?
    ''', (register_no,))
    
    # Determine current semester type (ODD/EVEN)
    current_semester_type = 'EVEN' if semester % 2 == 0 else 'ODD'
    
    # Query 2: Get subjects for hall ticket
    # - Current semester subjects (REGULAR status)
    # - Arrear subjects from arrears JSON array (ARREAR status)
    subjects = db.execute('''
        SELECT sub.subject_code, sub.subject_name,
               sch.exam_date, sch.session
        FROM subjects sub
        JOIN schedules sch ON sub.subject_id = sch.subject_id
        WHERE (
            -- Current semester subjects (enrolled)
            (sub.subject_id IN (
                SELECT subject_id FROM student_subjects 
                WHERE student_id = ?
            ) AND sub.semester_type = ?)
            OR
            -- Arrear subjects (from arrears array)
            sub.subject_code IN (arrears_list)
        )
        ORDER BY sch.exam_date, sub.subject_code
    ''', (student_id, current_semester_type))
    
    # Mark subjects as REGULAR or ARREAR
    for subject in subjects:
        subject['status'] = 'ARREAR' if subject_code in arrears else 'REGULAR'
    
    return {
        'student': student,
        'subjects': subjects
    }
```

**Key Features**:
- **Semester filtering**: Only shows current semester subjects (not both ODD and EVEN)
- **Arrear detection**: Checks subject_code against student's arrears JSON array
- **Status marking**: Clear REGULAR vs ARREAR labeling
- **Schedule integration**: Gets exam dates/sessions from schedules table
    seating = db.execute('''
        SELECT hall_no, seat_no
        FROM seating_allocations
        WHERE student_id = ? AND exam_type = ?
    ''', (student_id, exam_type))
    
    return {
        'student': student,
        'subjects': subjects,
        'seating': seating
    }
```

**Data Flow**: Database → Python Dict → HTML Template → PDF

---

#### 3. PDF Generation Algorithm

**Where**: [`server.py:200-250`](Hall Ticket Generation/v2_weasyprint/server.py#L200-L250)

**Why**: 
- Professional printable output
- Standard A4 format
- High-quality rendering

**How**:

```python
def generate_pdf(html_content):
    # Render HTML with CSS
    html = HTML(string=html_content)
    
    # Apply custom CSS
    css = CSS(string='''
        @page { 
            size: A4; 
            margin: 1cm; 
        }
        body { 
            font-family: 'Arial', sans-serif; 
        }
    ''')
    
    # Generate PDF
    pdf_bytes = html.write_pdf(stylesheets=[css])
    
    return pdf_bytes
```

**Uses**: WeasyPrint library for HTML-to-PDF conversion

---

#### 4. Examination Rules Display

**Where**: [`hall_ticket_template.html:150-200`](Hall Ticket Generation/v2_weasyprint/templates/hall_ticket_template.html#L150-L200)

**Why**: Students must be aware of exam hall discipline

**How**: 
- Static HTML section with 6-point instruction list
- Bordered box for visibility
- Clear formatting with numbering

**Instructions Include**:
1. Arrive 30 minutes before exam
2. Carry hall ticket and ID proof
3. Prohibited items list
4. No communication during exam
5. Follow invigilator instructions
6. No malpractice warning

---

## Database Integration

### Location
- **Setup Script**: `Exam Scheduling Algorithm/integrated_db_setup.py`
- **Database File**: `Exam Scheduling Algorithm/exam_scheduling.db`

### Schema Design

#### Why This Schema?

Designed for:
- **Normalized structure**: Minimize data redundancy
- **Referential integrity**: Foreign key relationships
- **Scalability**: Support multiple exam cycles
- **Query efficiency**: Indexed columns

### Tables

#### 1. `subjects` Table

```sql
CREATE TABLE subjects (
    subject_id INTEGER PRIMARY KEY,
    subject_code TEXT UNIQUE NOT NULL,
    subject_name TEXT NOT NULL,
    department TEXT NOT NULL,
    year INTEGER NOT NULL,
    semester_type TEXT NOT NULL,  -- 'ODD' or 'EVEN'
    subject_type TEXT NOT NULL,   -- 'Theory' or 'Lab'
    exam_type TEXT NOT NULL,      -- 'BOTH', 'SEMESTER', 'INTERNAL'
    student_count INTEGER DEFAULT 0
)
```

**Indexes**: `subject_code`, `department`, `year`

---

#### 2. `students` Table

```sql
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    reg_no TEXT UNIQUE NOT NULL,  -- Format: {YY}MLID{DD}{NNN}
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    year INTEGER NOT NULL,
    semester INTEGER NOT NULL,
    degree TEXT,
    branch_full TEXT,
    dob TEXT,
    gender TEXT,
    regulation TEXT
)
```

**Indexes**: `reg_no`, `department`, `year`

---

#### 3. `halls` Table

```sql
CREATE TABLE halls (
    hall_id INTEGER PRIMARY KEY,
    hall_name TEXT UNIQUE NOT NULL,
    capacity INTEGER NOT NULL,
    columns INTEGER NOT NULL,  -- Range: 4-6
    active INTEGER DEFAULT 1
)
```

**Column Constraint**: `columns` BETWEEN 4 AND 6

---

#### 4. `exam_cycles` Table

```sql
CREATE TABLE exam_cycles (
    cycle_id INTEGER PRIMARY KEY,
    exam_type TEXT NOT NULL,
    year_group INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    created_date TEXT,
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

#### 5. `schedules` Table

```sql
CREATE TABLE schedules (
    schedule_id INTEGER PRIMARY KEY,
    cycle_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_date TEXT NOT NULL,
    session TEXT NOT NULL,  -- 'FN' or 'AN'
    FOREIGN KEY (cycle_id) REFERENCES exam_cycles(cycle_id),
    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
)
```

**Relationships**: Many-to-one with `exam_cycles` and `subjects`

---

### Mock Data Generation Algorithm

**Where**: [`integrated_db_setup.py:250-420`](Exam Scheduling Algorithm/integrated_db_setup.py#L250-L420)

**Why**: 
- Testing and demonstration
- Realistic data distribution
- Department variations

**How**:

```python
def populate_students_data():
    departments = ['CSE', 'ECE', 'MECH', 'CIVIL', 'EEE']
    dept_codes = {
        'CIVIL': '01', 'ECE': '02', 'MECH': '03', 
        'EEE': '04', 'CSE': '05'
    }
    
    # Varying student counts per department
    student_counts = {
        'CSE': 120, 'ECE': 117, 'MECH': 130, 
        'CIVIL': 139, 'EEE': 148
    }
    
    for year in range(1, 5):  # Years 1-4
        joining_year = 2025 - (year - 1)
        year_2digit = joining_year % 100
        
        for dept in departments:
            count = student_counts[dept]
            dept_code = dept_codes[dept]
            
            for i in range(1, count + 1):
                # Generate register number: {YY}MLID{DD}{NNN}
                reg_no = f"{year_2digit}MLID{dept_code}{i:03d}"
                
                # Insert student
                insert_student(reg_no, name, dept, year, ...)
```

**Total Mock Data**:
- **Students**: 2,616 (654 per year)
- **Subjects**: 60 (Year 1: 25, Year 2: 35)
- **Halls**: 24 (capacity 28-35, columns 4-6)
- **Teachers**: 24

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.7 or higher
python --version

# Required packages
pip install -r requirements.txt
```

### Requirements

```txt
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
reportlab>=3.6.0
qrcode>=7.3.1
Pillow>=8.3.0
weasyprint>=53.0
Flask>=2.0.0
flask-cors>=3.0.10
pymongo>=3.12.0
python-dotenv>=0.19.0
```

### Database Setup

```bash
cd "Exam Scheduling Algorithm"
python integrated_db_setup.py
```

This creates `exam_scheduling.db` with all tables and mock data.

---For Internal: Select internal number (1/2)
4. Select year group (1-4)
5. Enter date range (excluding Sundays)
6. Review schedule
7. Modify if needed (COE authority)
8. Confirm and save to database
9. PDF generated automatically

**Output**: 
- Schedule saved in database with cycle_id
- Schedules table populated with exam dates/sessions
- PDF file: `exam_schedule_[TYPE]_year[X]_YYYYMMDD_HHMMSS.pdf`

**Database Changes**:
- `exam_cycles` table: New row with status 'ACTIVE'
- `schedules` table: Multiple rows linking subjects to dates/sessions
**Steps**:
1. SExam Scheduling Algorithm"
python seating_allocation.py
```

**Steps**:
1. Select exam type (Internal/SEM)
2. **For Internal:**
   - Shows list of existing internal exam cycles from database
   - Select cycle (e.g., "Cycle 5 - Year 2")
   - Shows available date/session slots (e.g., "20.12.2025 FN - 7 subjects, 154 students")
   - Select specific slot to allocate
3. **For SEM:**
   - Shows list of existing semester exam cycles
   - Select cycle and year/semester
   - Shows available date/session slots
   - Select specific slot to allocate
4. Select or add teachers
5. Select halls (manual or auto-optimize)
6. Confirm allocation
7. PDF generation for selected slot only

**Key Features**:
- **Slot-based allocation**: Only allocates students for selected date/session
- **No arrears for Internal**: Internal exams ignore arrears field
- **Arrear handling for SEM**: Includes students with arrears in selected subjects
- **Multiple allocations**: Can run multiple times for different slots

**Outputs**:
- Student seating PDF (hall-wise layouts for selected slot)
- Faculty PDF (teacher assignments)
- Database records in `seating_allocations` table

**Files Created**:
- `seating_student_YYYY-MM-DD_Y[X]_[TYPE].pdf`
- `seating_faculty_YYYY-MM-DD_Year[X]_[TYPE].pdf
python seating_allocation.py
```

**Steps**:
1. Select year and exam type
2. Select or add teachers
3. Select halls (manual or auto-optimize)
4. Confirm allocation
5. PDF generation

**Outputs**:
- Student seating PDF (hall-wise layouts)
- Faculty PDF (teacher  (format: YYMLIDDDDNNN)
- View hall ticket preview
- **Shows current semester subjects + arrears only**
- Download PDF
- QR code verification

**Subject Display Logic**:
- **REGULAR status**: Current semester subjects student is enrolled in
- **ARREAR status**: Subjects from arrears JSON array
- **Filtering**: Does not show opposite semester subjects
- **Example**: Sem 6 student sees only EVEN subjects + any ODD arrears
- `seating_pdfs/student_seating_Year_X_EXAMTYPE_YYYYMMDD_HHMMSS.pdf`
- `seating_pdfs/faculty_seating_Year_X_EXAMTYPE_YYYYMMDD_HHMMSS.pdf`
- `seating_allocation_report.xlsx`

---

### 3. Generate Hall Tickets

```bash
cd "Hall Ticket Generation/v2_weasyprint"
python server.py
```

**Access**: Open browser to `http://localhost:5000`

**Features**:
- Enter register number
- View hall ticket preview
- Download PDF
- QR code verification

---

## Algorithm Performance Analysis

### Exam Scheduling

| Metric | Value | Complexity |
|--------|-------|------------|
| Subjects | 60 | O(d × s) |
| Departments | 5 | d = 5 |
| Max subjects/dept | 7 | s = 7 |
| Available days | 6 | O(n) |
| Slots per day | 2 | - |
| Total operations | ~420 | O(35) |
| Time | < 1 second | - |

### Seating Allocation
+ DB save | O(d × s) | `scheduler.py:332-460` |
| Constraint Validation | Check conflicts | O(s²) | `scheduler.py:100-150` |
| Cycle Reading | Load existing schedules | O(1) | `seating_allocation.py:1695-1720` |
| Slot Filtering | Students per date/session | O(n) | `seating_allocation.py:1722-1750` |
| SEM Seating | 1 student/bench allocation | O(n) | `seating_allocation.py:173-252` |
| Internal Seating | 2 students/bench pairing | O(n) | `seating_allocation.py:258-356` |
| Hall Optimization | Minimize halls & waste | O(h log h + h²) | `seating_allocation.py:1233-1315` |
| Department Mixing | Ensure diversity | O(n) | Throughout allocation |
| Subject Filtering | Current semester + arrears | O(s) | `server.py:88-114`
| Department mixing | ≥2 per hall | O(n) |
| Total operations | ~2,616 | O(n) |
| PDF generation | 3-5 seconds | O(h) |

### Hall Optimization

| Strategy | Halls | Waste | Time |
|----------|-------|-------|------|
| Manual | 11-13 | 5-10% | - |
| Auto (largest first) | 12 | 6.4% | < 0.1s |
| Auto (smallest first) | 12 | 6.4% | < 0.1s |
| Optimized | 11 | 4.6% | < 0.2s |

---

## Key Algorithms Summary

| Algorithm | Purpose | Complexity | Location |
|-----------|---------|------------|----------|
| Date Generation | Create available dates | O(n) | `scheduler.py:21-52` |
| SEM Scheduling | Distribute exams evenly | O(d × s) | `scheduler.py:159-330` |
| Internal Scheduling | Compact exam packing | O(d × s) | `scheduler.py:332-460` |
| Constraint Validation | Check conflicts | O(s²) | `scheduler.py:100-150` |
| SEM Seating | 1 student/bench allocation | O(n) | `seating_allocation.py:173-252` |
| Internal Seating | 2 students/bench pairing | O(n) | `seating_allocation.py:258-356` |
| Hall Optimization | Minimize halls & waste | O(h log h + h²) | `seating_allocation.py:1233-1315` |
| Department Mixing | Ensure diversity | O(n) | Throughout allocation |
| QR Generation | Create verification codes | O(1) | `server.py:75-95` |

**LegendSlot-Based Allocation?

- **Scalability**: Can allocate 150 students per slot instead of 700+ at once
- **Flexibility**: Different halls/teachers for different time slots
- **Resource optimization**: Don't need all halls at once
- **Realistic**: Matches actual exam center operations
- **Database-driven**: Single source of truth (main.py creates, seating reads)

### Why Separate Schedule Creation?

- **Single source of truth**: Schedule created once in main.py
- **Consistency**: Seating allocation reads from same database
- **Auditability**: Clear record of when/how schedule was created
- **Authority control**: COE creates schedule, administrators handle allocation
- **No duplication**: Prevents conflicting schedules

### Why Filter Hall Tickets?

- **Clarity**: Students only see relevant exam information
- **Accuracy**: Prevents confusion about which subjects to study
- **Compliance**: Matches actual exam participation
- **Performance**: Smaller PDFs load faster
- Each student has different subjects (current + their specific arrears)ed
- **Portable**: Single file database
- **ACID compliant**: Transaction safety
- **Zero configuration**: Works out of the box
- **Sufficient scale**: Handles 10,000+ students easily

### Why Randomization with Seed?

- **Fairness**: No favoritism
- **Reproducibility**: Same seed = same allocation
- **Unpredictability**: Students can't predict seating
- **Auditability**: Can regenerate exact same allocation

### Why Department Mixing?

- **Anti-cheating**: Primary security measure
- **Fair distribution**: No department clustering
- **Psychological deterrent**: Students see mixed departments
- **Compliance**: Meets university examination guidelines

### Why Separate PDFs?

- **Student PDF**: Visual hall layouts for students
- **Faculty PDF**: Summary tables for invigilators  
- **Excel**: Detailed data for administration
- Each serves different stakeholder needs

---

## Contributing

To extend this system:

1. **Add new constraints**: Modify `validate_constraints()` in `scheduler.py`
2. **Change seating algorithm**: Update `_allocate_sem_linear_optimized()` or `_allocate_internal_alternating_optimized()`
3. **Enhance hall tickets**: Edit `hall_ticket_template.html`
4. **Add new reports**: Create new PDF generation functions

---

## License

Educational use only. Property of Marri Laxman Reddy Institute of Technology.

---

## Authors

Developed as part of One-Stop Hackathon Project, December 2025.

---

## Support

For issues or questions, refer to:
- Database: `integrated_db_setup.py` comments
- Scheduling: `scheduler.py` docstrings
- Seating: `seating_allocation.py` inline documentation
- Hall Tickets: `server.py` API documentation
