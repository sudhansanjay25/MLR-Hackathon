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

### Phase 3: Conflict Detection
- Build conflict graph
- Subjects from same department = CONFLICT
- Different departments = NO CONFLICT

### Phase 4: Greedy Scheduling
- Assign subjects to earliest available slots
- Validate gap constraints
- If constraint violated but slot available, assign anyway and log violation
- If no slots available, report error

### Phase 5: Output Generation
- Save schedule to database
- Log violations
- Display formatted timetable

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
- Professional formatted timetable with:
  - Title and metadata
  - Schedule summary
  - Complete timetable with dates, sessions, subjects
  - Constraint violations (if any)
  - Department-wise summary
- Generated using ReportLab library
- Landscape A4 format for better readability
- Filename format: `exam_schedule_[type]_year[X]_[timestamp].pdf`

## Sample Output

```
======================================================================
  SEMESTER EXAM SCHEDULE - Year 2
======================================================================

   Total Exams Scheduled: 19
   Constraint Violations: 13

----------------------------------------------------------------------
Date            Session    Dept     Code       Subject                  
----------------------------------------------------------------------
16.12.2025      FN         CSE      CS306      Software Engineering         
16.12.2025      FN         ECE      EC305      Communication Systems     
16.12.2025      FN         MECH     ME305      Material Science          
----------------------------------------------------------------------

   ✅ PDF generated: exam_schedule_semester_year2_20251211_143052.pdf
```

## Future Enhancements

- Web interface integration with Flask
- PDF/Excel export of schedules
- Room allocation based on capacity
- Invigilator duty assignment
- Student hall ticket integration
- Multi-department common subjects handling
