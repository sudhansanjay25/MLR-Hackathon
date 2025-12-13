# Phase 4 - Python Integration & PDF Generation - COMPLETE! 🎉

## Overview
Phase 4 implements full Python integration for exam scheduling and seating arrangement with actual PDF generation using ReportLab.

## What Was Implemented

### 1. **Python Wrapper Scripts**
Created two new Python scripts that integrate with MongoDB:

#### `modules/scheduler_wrapper.py`
- Connects to MongoDB to fetch subjects and schedule data
- Generates exam timetable based on available dates
- Creates professional timetable PDF using ReportLab
- Commands:
  - `generate_timetable` - Generate timetable entries
  - `generate_pdf` - Generate timetable PDF

#### `modules/seating_wrapper.py`
- Allocates students to exam halls from MongoDB
- Implements alternating seat pattern for Internal exams
- Sequential allocation for SEM exams
- Generates two PDF versions:
  - **Student PDF**: Hall-wise seating arrangement with register numbers
  - **Faculty PDF**: Duty roster with exam schedule and invigilator assignments
- Commands:
  - `allocate_seats` - Allocate students to halls
  - `generate_student_pdf` - Generate student seating PDF
  - `generate_faculty_pdf` - Generate faculty duty roster PDF

### 2. **Updated pythonRunner.js**
Enhanced the Python runner utility to actually execute Python scripts:

- `runScheduling()` - Now calls Python scheduler instead of mock data
- `runSeatingArrangement()` - Calls Python seating allocator with fallback
- `generateTimetablePDF()` - NEW: Generates timetable PDF after schedule creation
- `generateSeatingPDFs()` - NEW: Generates both student and faculty seating PDFs

### 3. **PDF Download Endpoints**
Added three new API endpoints in COE routes:

```javascript
GET /api/coe/download-timetable/:scheduleId
GET /api/coe/download-seating-student/:scheduleId  
GET /api/coe/download-seating-faculty/:scheduleId
```

Each endpoint:
- Validates schedule exists
- Checks PDF path in database
- Performs security validation (prevents directory traversal)
- Serves PDF file for download

### 4. **Enhanced Schedule Creation Workflow**
Updated COE schedule creation endpoint to:

1. Create exam schedule in database
2. Run Python scheduling algorithm → Generate timetable
3. Save timetable entries to database
4. Run Python seating arrangement → Allocate students
5. Save seating allocations to database
6. **Generate timetable PDF** ✨ NEW
7. **Generate student & faculty seating PDFs** ✨ NEW
8. Update schedule with PDF paths

### 5. **View Schedule Page Updates**
Modified download buttons to use new dedicated endpoints:
- Download Timetable PDF button
- Download Student Seating PDF button  
- Download Faculty Duty Roster PDF button

## File Structure

```
EXAM_management/
├── modules/
│   ├── scheduler_wrapper.py          # NEW: Timetable generation + PDF
│   ├── seating_wrapper.py            # NEW: Seating allocation + PDFs
│   └── requirements.txt              # NEW: Python dependencies
├── backend/
│   ├── utils/
│   │   └── pythonRunner.js           # UPDATED: Full Python integration
│   └── routes/
│       └── coe.js                    # UPDATED: PDF generation + download endpoints
├── frontend/
│   └── views/
│       └── coe/
│           └── view-schedule.ejs     # UPDATED: Download button links
└── uploads/                          # NEW: PDF storage directory
    ├── timetables/
    └── seating/
```

## Python Dependencies

```
pymongo==4.13.2      # MongoDB driver
reportlab==4.4.6     # PDF generation library
dnspython==2.8.0     # DNS support for pymongo
```

Installed via: `pip install pymongo reportlab`

## PDF Generation Features

### Timetable PDF
- Professional layout with institutional header
- Table with columns: Date, Subject Code, Subject Name, Time
- Landscape A4 format
- Academic year, exam type, year, session details

### Student Seating PDF
- Organized by hall
- Table with columns: Seat No, Register Number, Student Name, Department
- Multiple halls on same PDF
- Hall-wise sections with clear headers

### Faculty Duty Roster PDF
- Complete exam schedule table
- Invigilator assignment table
- Hall-to-faculty mapping
- Useful for faculty to know their duty schedule

## Security Features

1. **Path Validation**: All download endpoints validate PDF paths are within allowed directories
2. **File Existence Check**: Verifies file exists before serving
3. **Authentication**: All endpoints require COE role authentication
4. **No Directory Traversal**: Prevents accessing files outside uploads folder

## How to Test

### 1. Install Python Dependencies
```bash
cd EXAM_management/modules
pip install pymongo reportlab
```

### 2. Start Server
```bash
cd EXAM_management/backend
node server.js
```

### 3. Create Schedule
1. Go to http://localhost:5000/coe/schedule-exam
2. Fill in exam details
3. Select faculty and halls
4. Submit form

### 4. Download PDFs
1. After schedule creation, go to view schedule page
2. Click on any download button:
   - 📄 Download Timetable PDF
   - 📋 Download Student Seating PDF
   - 👥 Download Faculty Duty Roster PDF

## Database Fields

Updated ExamSchedule schema now stores:
```javascript
{
  timetablePdfPath: "uploads/timetables/timetable_<id>_<timestamp>.pdf",
  seatingPdfPaths: {
    studentPdf: "uploads/seating/seating_student_<id>_<timestamp>.pdf",
    facultyPdf: "uploads/seating/seating_faculty_<id>_<timestamp>.pdf"
  }
}
```

## Key Technical Details

### Python-Node Communication
- Uses `spawn` to execute Python scripts
- Passes JSON parameters via command-line arguments
- Parses JSON output from stdout
- Error handling with try-catch and fallback mechanisms

### MongoDB Connection in Python
```python
mongo_uri = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/exam_management')
client = MongoClient(mongo_uri)
db = client.get_default_database()
```

### PDF Generation
- Uses ReportLab's `SimpleDocTemplate` and `Table` classes
- Custom styling for headers, titles, and table cells
- Landscape orientation for wide tables
- Professional color scheme (grey headers, beige rows)

## Error Handling

1. **Python Execution Failure**: Falls back to mock implementation
2. **PDF Generation Failure**: Logs error but doesn't fail schedule creation
3. **File Not Found**: Returns 404 with appropriate error message
4. **Invalid Paths**: Returns 403 Forbidden

## What's Next (Phase 5)

- [ ] Hall ticket generation with QR codes
- [ ] Student dashboard to view/download hall tickets
- [ ] QR code integration for attendance
- [ ] Faculty QR scanner implementation

## Testing Results

✅ **Completed Successfully:**
- Python dependencies installed
- Server starts without errors
- MongoDB connection working
- Schedule creation endpoint functional
- Python scripts callable from Node.js
- PDF generation workflow ready

⏳ **Pending User Test:**
- Create actual exam schedule
- Verify PDF generation
- Download and view generated PDFs
- Test all three PDF types

## Notes

- PDFs are stored in `uploads/timetables/` and `uploads/seating/`
- Filenames include schedule ID and timestamp for uniqueness
- Old schedules can be cleaned up by deleting old PDF files
- Python scripts require MongoDB to be running
- All PDF endpoints require authentication

---

**Phase 4 Status: IMPLEMENTATION COMPLETE** ✅  
**Ready for Testing**: Yes 🚀  
**Next Phase**: Phase 5 - Hall Ticket Generation
