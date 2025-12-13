# Phase 4 - Quick Reference Guide

## Commands to Get Started

### 1. Install Python Dependencies (One-time)
```bash
cd EXAM_management/modules
pip install pymongo reportlab
```

### 2. Start Server
```bash
cd EXAM_management/backend
node server.js
```

### 3. Access Application
- COE Dashboard: http://localhost:5000/coe/dashboard
- Schedule Exam: http://localhost:5000/coe/schedule-exam
- View Schedules: http://localhost:5000/coe/view-schedules

## Testing PDF Generation

### Create a Test Schedule:
1. Open: http://localhost:5000/coe/schedule-exam
2. Fill in:
   - Academic Year: 2024-2025
   - Exam Type: Internal1
   - Year: 2
   - Dates: Dec 13-20, 2025
   - Holiday: Dec 14, 2025
   - Select 5+ faculty
   - Select 8+ halls
3. Submit form
4. Wait for success message

### Download PDFs:
1. Go to "View All Schedules"
2. Click "View Details" for your schedule
3. Click download buttons:
   - 📄 **Timetable PDF**: Shows exam dates, subjects, timings
   - 📋 **Student Seating PDF**: Shows hall-wise seat allocations
   - 👥 **Faculty Duty PDF**: Shows invigilator duty roster

## API Endpoints

### Schedule Creation
```
POST /api/coe/schedule-exam
Body: { academicYear, examType, year, session, startDate, endDate, holidays, selectedFaculty[], selectedHalls[] }
```

### PDF Downloads
```
GET /api/coe/download-timetable/:scheduleId
GET /api/coe/download-seating-student/:scheduleId
GET /api/coe/download-seating-faculty/:scheduleId
```

## What Phase 4 Does

1. **Python Integration**: Calls actual Python scripts instead of mock data
2. **Timetable Generation**: Creates exam schedule avoiding weekends/holidays
3. **Seating Allocation**: Assigns students to halls with seat numbers
4. **PDF Generation**: Creates 3 professional PDFs:
   - Timetable with institutional header
   - Student seating arrangement by hall
   - Faculty duty roster with assignments

## File Locations

### Python Scripts
- `modules/scheduler_wrapper.py` - Timetable generation
- `modules/seating_wrapper.py` - Seating allocation

### Generated PDFs
- `uploads/timetables/` - Timetable PDFs
- `uploads/seating/` - Seating arrangement PDFs

### Configuration
- `.env` - Environment variables (MongoDB URI, Python path)
- `modules/requirements.txt` - Python dependencies

## Troubleshooting

### "Python not found"
- Install Python 3.8+ from python.org
- Add Python to PATH
- Run: `python --version` to verify

### "Module not found: pymongo"
- Run: `pip install pymongo reportlab`
- Verify: `pip list | findstr pymongo`

### "MongoDB connection failed"
- Ensure MongoDB is running on localhost:27017
- Check `.env` file has correct MONGO_URI

### "PDF not downloading"
- Check server logs for Python errors
- Verify Python dependencies are installed
- Check `uploads/` folder permissions

## Next Steps

✅ Phase 4 Complete - Python Integration & PDF Generation  
🔄 Ready to test with actual exam schedule  
⏭️ Phase 5 Next - Hall Ticket Generation with QR codes

## Need Help?

Check these files for details:
- `PHASE4_COMPLETE.md` - Full documentation
- `backend/utils/pythonRunner.js` - Python integration code
- `modules/scheduler_wrapper.py` - Scheduler implementation
- `modules/seating_wrapper.py` - Seating implementation
