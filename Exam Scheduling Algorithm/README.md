# Exam Scheduling Algorithm

Automated exam timetable generation system with constraint handling for college examinations.

## Features

- **Two Exam Types**: Semester (3 hours) and Internal (1.5 hours)
- **Constraint-Based Scheduling**: Handles gap requirements between exams
- **Department-wise Scheduling**: Independent scheduling per department
- **Conflict Detection**: Prevents same department students from having concurrent exams
- **Holiday Management**: Excludes weekends and custom holidays
- **Violation Reporting**: Reports when constraints cannot be satisfied

## Database Schema

### Tables:
1. **students** - Student information
2. **subjects** - Subject details with classification (HEAVY/NONMAJOR)
3. **exam_cycles** - Exam scheduling sessions
4. **exam_schedule** - Generated timetables
5. **holidays** - Holiday exclusions
6. **schedule_violations** - Constraint violation logs

## Gap Constraints

### Semester Exams:
- **Heavy subjects**: Minimum 1 full day gap
- **Non-major subjects**: Minimum half-day gap (different session or next day)
- **AN session rule**: If exam in AN, next exam must be AN (next day) or day after tomorrow

### Internal Exams:
- Single session per day (8:30 AM - 10:00 AM)
- No gap constraints

## Files

- `db_setup.py` - Database creation and mock data population
- `config.py` - Configuration constants
- `scheduler.py` - Core scheduling algorithm
- `main.py` - Command-line interface
- `pdf_generator.py` - PDF export functionality using ReportLab
- `test_demo.py` - Automated test suite
- `usage_examples.py` - Programmatic usage examples

## Usage

### 1. Setup Database
```bash
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\ht\Scripts"
.\activate
cd "c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\Exam Scheduling Algorithm"
python db_setup.py
```

### 2. Run Scheduler
```bash
python main.py
```

Follow the prompts to:
1. Select exam type (Semester/Internal)
2. Choose year group (1-4)
3. Enter date range
4. Specify holidays to exclude

## Algorithm Logic

### Phase 1: Date Preparation
- Generate available dates from range
- Exclude weekends (Saturday, Sunday)
- Exclude admin-specified holidays

### Phase 2: Subject Loading
- Fetch subjects for selected year and exam type
- Group by department
- Sort by subject type (HEAVY first)

### Phase 3: Date-Based Conflict Prevention
- **Critical Rule**: Maximum one exam per department per day
- Uses `dept_date_usage` dictionary to track department usage by date
- Prevents scheduling conflicts within departments
- Different departments can have exams on same day

### Phase 4: Greedy Scheduling
- Assign subjects to earliest available dates
- Validate gap constraints (semester exams only)
- Respect one-exam-per-department-per-day rule
- If constraint violated but slot available, assign anyway and log violation
- If no slots available, report error and suggest extending date range

### Phase 5: Output Generation
- Save schedule to database with cycle tracking
- Log constraint violations with details
- Display formatted timetable in console
- Auto-generate PDF in appropriate format (portrait/landscape)

## Mock Data

### Departments: CSE, ECE, MECH
### Year: 2 (Second Year)
### Subjects per Department:
- **CSE**: 8 subjects (5 HEAVY, 3 NONMAJOR)
- **ECE**: 7 subjects (4 HEAVY, 3 NONMAJOR)
- **MECH**: 7 subjects (4 HEAVY, 3 NONMAJOR)

### Students: 20 per department (60 total)

## Output Formats

The system generates schedules in two formats:

### 1. Console Output
Formatted text table displayed in terminal during execution

### 2. PDF Document (Automatic)
Professional formatted timetable with institutional format:

#### Semester Exams:
- **Portrait A4 orientation**
- Department-wise tables with separate sections
- Columns: Date, Session, Subject Code, Subject Name
- White background with black text and borders
- Tables kept together on pages when possible

#### Internal Exams:
- **Landscape A4 orientation**
- Matrix format (Departments × Dates) on single page
- Departments in rows, dates in columns
- No subject codes displayed
- Date headers include day name (e.g., "02.12.2025\nTuesday")
- Automatic word wrapping for long subject names
- Complete words move to next line (no character splitting)
- White background with black text and borders

**Features:**
- Institutional header with college details
- Clean, professional design
- Constraint violations summary (if any)
- Generated using ReportLab library
- Filename format: `exam_schedule_[type]_year[X]_[timestamp].pdf`

## Sample Output

```
======================================================================
  SEMESTER EXAM SCHEDULE - Year 2
======================================================================

   Total Exams Scheduled: 19
   Constraint Violations: 10

----------------------------------------------------------------------
Date            Session    Dept     Code       Subject                  
----------------------------------------------------------------------
16.12.2025      FN         CSE      CS306      Software Engineering         
16.12.2025      FN         ECE      EC305      Communication Systems     
16.12.2025      FN         MECH     ME305      Material Science          
17.12.2025      FN         CSE      CS307      Web Technologies
----------------------------------------------------------------------

📄 Generating PDF...
   ✅ PDF saved: exam_schedule_semester_year2_20251211_143052.pdf
```

## Testing

Run the automated test suite:
```bash
python test_demo.py
```

Tests include:
- ✅ Semester exam scheduling with gap constraints
- ✅ Internal exam scheduling 
- ✅ Edge case handling (insufficient dates)
- ✅ PDF generation for both formats
- ✅ Violation detection and reporting

## Key Features Implemented

### ✅ Conflict-Free Scheduling
- One exam per department per day (enforced)
- No overlapping exams for same department students

### ✅ Dual PDF Formats
- Portrait tables for semester exams
- Landscape matrix for internal exams

### ✅ Smart Text Handling
- Automatic word wrapping in table cells
- Complete words stay together (no character splitting)
- Date and day displayed in same cell

### ✅ Professional Output
- Institutional header formatting
- Clean white background design
- Constraint violation reporting

## Future Enhancements

- Web interface with Flask/Django
- Room allocation based on capacity
- Invigilator duty assignment
- Student hall ticket generation
- Email notifications
- Calendar export (iCal format)
- Multi-department common subjects handling
