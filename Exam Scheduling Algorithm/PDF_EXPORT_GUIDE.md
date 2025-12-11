# PDF Export Feature - Documentation

## Overview

The exam scheduling system automatically generates professional PDF timetables using the ReportLab library.

## PDF Features

### 1. **Title Section**
- Exam type (SEMESTER/INTERNAL EXAMINATION SCHEDULE)
- Year and date period
- Generation timestamp

### 2. **Schedule Summary**
- Total exams scheduled
- Number of constraint violations
- List of departments

### 3. **Complete Timetable Table**
Formatted table with columns:
- **Semester Exams**: Date | Session | Time | Dept | Code | Subject Name | Type
- **Internal Exams**: Date | Time | Dept | Code | Subject Name | Type

Features:
- Color-coded header (blue)
- Alternating row backgrounds for readability
- Grid lines for clarity
- Landscape orientation for better fit

### 4. **Constraint Violations Table** (if any)
- Subject code
- Severity level
- Issue description
- Red header to highlight warnings

### 5. **Department-wise Summary**
- Department name
- Total exams
- Heavy subjects count
- Non-major subjects count

## File Naming Convention

**Automatic naming**:
```
exam_schedule_[type]_year[X]_[timestamp].pdf
```

Examples:
- `exam_schedule_semester_year2_20251211_143052.pdf`
- `exam_schedule_internal_year3_20251211_150230.pdf`

**Custom naming** (programmatic):
```python
from pdf_generator import generate_schedule_pdf

pdf_path = generate_schedule_pdf(
    schedule, violations, 'SEMESTER', 2,
    '12.12.2025', '28.12.2025',
    filename='my_custom_schedule.pdf'  # Custom name
)
```

## Color Scheme

- **Headers**: Dark Blue (#2c5282)
- **Violation Headers**: Red (#c53030)
- **Background**: White with light gray alternating rows (#f7fafc)
- **Text**: Black for body, White for headers

## Layout Specifications

- **Page Size**: A4 Landscape (297mm × 210mm)
- **Margins**: 30pt (all sides), 50pt top
- **Font**: Helvetica / Helvetica-Bold
- **Font Sizes**: 
  - Title: 24pt
  - Headings: 16pt
  - Table Headers: 10pt
  - Body Text: 9-10pt

## Usage in CLI

When you run `main.py`, PDF generation happens automatically after successful scheduling:

```
======================================================================
   Schedule saved to database (Cycle ID: 5)
======================================================================

   Generating PDF...
   ✅ PDF generated: C:\Path\To\exam_schedule_semester_year2_20251211_143052.pdf
```

## Error Handling

If PDF generation fails (e.g., ReportLab not installed), the system:
1. Displays a warning message
2. **Still saves the schedule to database**
3. Continues execution without crashing

Example:
```
   ⚠️  PDF generation failed: No module named 'reportlab'
   Schedule is still saved in database.
```

## Requirements

- **reportlab** library (already installed in ht venv)
- Available disk space for PDF files (typically 50-200 KB per file)

## Sample PDFs Generated

After running `test_demo.py`, you'll find:
- `test_semester_schedule.pdf` - Semester exam schedule
- `test_internal_schedule.pdf` - Internal exam schedule

## Programmatic Access

```python
from scheduler import ExamScheduler
from pdf_generator import generate_schedule_pdf

# Schedule exams
scheduler = ExamScheduler()
schedule, violations = scheduler.schedule_semester_exams(
    year=2, 
    start_date='12.12.2025', 
    end_date='28.12.2025',
    holidays=['20.12.2025']
)

# Generate PDF
pdf_path = generate_schedule_pdf(
    schedule=schedule,
    violations=violations,
    exam_type='SEMESTER',
    year=2,
    start_date='12.12.2025',
    end_date='28.12.2025',
    filename='custom_schedule.pdf'  # Optional
)

print(f"PDF saved: {pdf_path}")
scheduler.close()
```

## PDF Content Example

```
╔════════════════════════════════════════════════════════════════╗
║          SEMESTER EXAMINATION SCHEDULE                         ║
║                                                                ║
║  Year: 2          Period: 12.12.2025 to 28.12.2025           ║
║  Generated on: 11.12.2025 14:30:52                           ║
╚════════════════════════════════════════════════════════════════╝

SCHEDULE SUMMARY
─────────────────────────────────────────────────────────────────
Total Exams Scheduled: 19
Constraint Violations: 13
Departments: CSE, ECE, MECH

EXAMINATION TIMETABLE
─────────────────────────────────────────────────────────────────
┌──────────┬─────────┬──────────────────┬──────┬────────┬────────────────────┬──────────┐
│   Date   │ Session │       Time       │ Dept │  Code  │    Subject Name    │   Type   │
├──────────┼─────────┼──────────────────┼──────┼────────┼────────────────────┼──────────┤
│12.12.2025│   FN    │ 10:00 AM-1:00 PM │ CSE  │ CS306  │ Software Eng...    │ NONMAJOR │
│          │   FN    │ 10:00 AM-1:00 PM │ ECE  │ EC305  │ Communication...   │ NONMAJOR │
│          │   FN    │ 10:00 AM-1:00 PM │ MECH │ ME305  │ Material Science   │ NONMAJOR │
│          │   AN    │  2:00 PM-5:00 PM │ CSE  │ CS307  │ Web Technologies   │ NONMAJOR │
...
└──────────┴─────────┴──────────────────┴──────┴────────┴────────────────────┴──────────┘

CONSTRAINT VIOLATIONS
─────────────────────────────────────────────────────────────────
⚠️ 13 constraint violation(s) detected. These occur due to 
insufficient time slots or tight scheduling requirements.

┌────────────┬────────────┬─────────────────────────────────────────┐
│Subject Code│  Severity  │         Issue Description               │
├────────────┼────────────┼─────────────────────────────────────────┤
│   CS301    │   MEDIUM   │ Cannot schedule FN next day after AN... │
│   CS302    │   MEDIUM   │ Heavy subject needs 1 full day gap...   │
...
└────────────┴────────────┴─────────────────────────────────────────┘

DEPARTMENT-WISE SUMMARY
─────────────────────────────────────────────────────────────────
┌────────────┬─────────────┬────────────────┬───────────────────┐
│ Department │ Total Exams │ Heavy Subjects │ Non-Major Subjects│
├────────────┼─────────────┼────────────────┼───────────────────┤
│    CSE     │      7      │       5        │         2         │
│    ECE     │      6      │       4        │         2         │
│    MECH    │      6      │       4        │         2         │
└────────────┴─────────────┴────────────────┴───────────────────┘
```

## Distribution

PDF files can be:
- Emailed to administrators
- Printed for notice boards
- Shared with faculty departments
- Archived for record-keeping
- Attached to hall ticket generation system

## Future Enhancements

Potential additions:
- Department-specific PDFs (one per department)
- Room allocation in PDF
- Invigilator duty roster
- Student-wise exam list
- QR code for digital verification
- Watermarking for official documents
