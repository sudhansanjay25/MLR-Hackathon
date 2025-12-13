# EXAM Management System - Complete Setup Guide

## ✅ Project Status: FULLY FUNCTIONAL

All phases (1-5) have been completed and the system is now fully operational with MongoDB integration.

---

## 🎉 What's Been Fixed and Completed

### 1. **Database Connection & Authentication** ✅
- Fixed MongoDB connection (removed deprecated options)
- Updated authentication to use MongoDB instead of in-memory users
- Created proper `.env` configuration
- Seeded database with test data (60 students, 10 subjects, 4 halls, 3 faculty)

### 2. **All Database Models Completed** ✅
- User (COE, Faculty, Student)
- Department
- Hall
- Subject
- ExamSchedule
- ExamTimetable
- SeatingAllocation
- HallTicket
- Attendance

### 3. **Backend Routes Completed** ✅
- **COE Routes**: Dashboard, schedule exam, view schedules, authorize hall tickets, generate PDFs
- **Faculty Routes**: Dashboard, view assignments, mark attendance
- **Student Routes**: Dashboard, view schedule, download hall ticket, check attendance

### 4. **Python Integration** ✅
- Updated pythonRunner.js to use correct wrapper paths
- Scheduler wrapper: `modules/scheduler_wrapper.py`
- Seating wrapper: `modules/seating_wrapper.py`
- Hall ticket wrapper: `modules/hall_ticket_wrapper.py`

---

## 🚀 How to Run the Project

### Prerequisites
- **Node.js** v16+ installed
- **MongoDB** running on localhost:27017
- **Python 3.x** with virtual environment at `../ht/`

### Step 1: Install Node Dependencies
```bash
cd EXAM_management
npm install
```

### Step 2: Seed the Database
```bash
node seed.js
```

**Output:**
```
✓ MongoDB Connected
✓ Users seeded
✓ Departments seeded
✓ Halls seeded
✓ Subjects seeded
✓ 60 Students seeded

✅ Database seeding completed successfully!
```

### Step 3: Start the Server
```bash
cd backend
node server.js
```

**Output:**
```
============================================================
🚀 EXAM MANAGEMENT SYSTEM
============================================================
✓ Server running on http://localhost:5000
✓ Environment: development
============================================================
✓ MongoDB Connected: localhost
✓ Database: exam_management
```

### Step 4: Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🔑 Login Credentials

### COE (Controller of Examinations)
- **Email**: `coe@mlrit.ac.in`
- **Password**: `coe123`

### Faculty
- **Email**: `faculty001@mlrit.ac.in`
- **Password**: `faculty123`

### Student
- **Email**: `714025104001@mlrit.ac.in`
- **Password**: `student123`

---

## 📋 Features Available

### COE Dashboard Features:
1. **Schedule Exam**
   - Select academic year, exam type (Internal/SEM), year, semester
   - Choose start/end dates and holidays
   - Assign faculty and halls
   - System automatically:
     - Generates exam timetable
     - Allocates students to halls
     - Creates PDF documents

2. **View Schedules**
   - See all created exam schedules
   - View detailed timetable
   - Download timetable PDF
   - Download seating arrangement PDFs (student & faculty versions)

3. **Authorize Hall Tickets**
   - Authorize hall tickets for a specific schedule
   - System automatically generates hall tickets for all students

4. **Generate Hall Tickets**
   - Single hall ticket generation
   - Bulk hall ticket generation by year

### Faculty Dashboard Features:
1. **View Assigned Exams**
   - See exams where you're assigned as invigilator
   - View hall assignments
   - Check exam dates and times

2. **Mark Attendance**
   - Mark student attendance via QR code or manual entry
   - View attendance records

### Student Dashboard Features:
1. **View Exam Schedule**
   - See your exam timetable
   - View exam dates and subjects

2. **Download Hall Ticket**
   - Download your authorized hall ticket
   - Hall ticket includes QR code for verification

3. **Check Seating Allocation**
   - View your assigned hall and seat number

4. **View Attendance**
   - Check your attendance records

---

## 📁 Project Structure

```
EXAM_management/
├── backend/
│   ├── config/
│   │   └── db.js                 # MongoDB connection
│   ├── models/                    # All Mongoose schemas
│   │   ├── User.js
│   │   ├── Student.js
│   │   ├── Department.js
│   │   ├── Hall.js
│   │   ├── Subject.js
│   │   ├── ExamSchedule.js
│   │   ├── ExamTimetable.js
│   │   ├── SeatingAllocation.js
│   │   ├── HallTicket.js
│   │   └── Attendance.js
│   ├── routes/                    # API routes
│   │   ├── auth.js               # Login/logout
│   │   ├── coe.js                # COE operations
│   │   ├── faculty.js            # Faculty operations
│   │   └── student.js            # Student operations
│   ├── middleware/
│   │   └── auth.js               # JWT authentication
│   ├── utils/
│   │   └── pythonRunner.js       # Python integration
│   └── server.js                 # Express server
├── frontend/
│   ├── views/
│   │   ├── auth/
│   │   │   └── login.ejs
│   │   ├── coe/
│   │   │   ├── dashboard.ejs
│   │   │   ├── schedule-exam.ejs
│   │   │   ├── view-schedules.ejs
│   │   │   └── view-schedule.ejs
│   │   ├── faculty/
│   │   │   └── dashboard.ejs
│   │   └── student/
│   │       └── dashboard.ejs
│   └── public/                    # Static assets
├── modules/                       # Python wrappers
│   ├── scheduler_wrapper.py
│   ├── seating_wrapper.py
│   └── hall_ticket_wrapper.py
├── outputs/                       # Generated PDFs
│   ├── timetables/
│   ├── seating/
│   └── hall_tickets/
├── .env                          # Environment variables
├── seed.js                       # Database seeder
└── package.json
```

---

## 🔄 Complete Workflow

### 1. COE Creates Exam Schedule
1. Login as COE
2. Go to "Schedule Exam"
3. Fill in exam details:
   - Academic Year: 2024-2025
   - Exam Type: Internal or SEM
   - Year: 1-4
   - Semester: 1-8
   - Start Date, End Date
   - Holidays (optional)
   - Select Faculty (invigilators)
   - Select Halls
4. Submit

**Backend Process:**
- Creates ExamSchedule in MongoDB
- Runs Python scheduler to generate timetable
- Saves ExamTimetable entries
- Runs Python seating allocator
- Saves SeatingAllocation entries
- Generates timetable PDF
- Generates seating PDFs (student & faculty)

### 2. COE Authorizes Hall Tickets
1. Go to "View Schedules"
2. Click on a schedule
3. Click "Authorize Hall Tickets"

**Backend Process:**
- Marks schedule as authorized
- Generates hall tickets for all students
- Creates HallTicket entries in MongoDB
- Generates PDF hall tickets with QR codes

### 3. Faculty Views Assignment
1. Login as Faculty
2. Dashboard shows assigned exams
3. View seating arrangements
4. Mark attendance during exam

### 4. Student Views Details
1. Login as Student
2. Dashboard shows upcoming exams
3. View exam timetable
4. Check seating allocation
5. Download hall ticket (once authorized)
6. View attendance records

---

## 🛠️ Technical Details

### MongoDB Collections
- users
- students
- departments
- halls
- subjects
- examschedules
- examtimetables
- seatingallocations
- halltickets
- attendances

### Environment Variables (.env)
```env
MONGO_URI=mongodb://localhost:27017/exam_management
PORT=5000
NODE_ENV=development
JWT_SECRET=exam_management_secret_key_2025_mlrit_secure_token
PYTHON_PATH=C:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\ht\Scripts\python.exe
```

### Python Dependencies (in ht venv)
- pymongo
- reportlab
- qrcode
- Pillow
- matplotlib

---

## 🐛 Troubleshooting

### Issue: "Invalid credentials" on login
**Solution**: Make sure you ran `node seed.js` to create test users in the database.

### Issue: Server won't start
**Solution**: 
1. Check if MongoDB is running
2. Check if port 5000 is available
3. Kill any existing node processes: `Get-Process node | Stop-Process`

### Issue: Python scripts fail
**Solution**:
1. Verify Python path in `.env`
2. Check if ht virtual environment has required packages
3. Activate venv: `..\ht\Scripts\activate`
4. Install packages: `pip install pymongo reportlab qrcode Pillow matplotlib`

### Issue: PDFs not generating
**Solution**:
1. Check if `outputs/` folders exist
2. Verify Python wrapper paths in `pythonRunner.js`
3. Check MongoDB has schedule data

---

## ✨ Key Improvements Made

1. **Fixed all incomplete models** - All schemas now properly export Mongoose models
2. **Database integration** - All routes now use MongoDB instead of mock data
3. **Authentication** - Uses real user authentication with JWT
4. **Python integration** - Correctly paths to wrapper scripts in modules folder
5. **PDF generation** - Properly saves PDF paths to database
6. **Error handling** - Added proper error handling throughout
7. **Seeding** - Created comprehensive seed script with 60 students, multiple departments

---

## 📝 Next Steps (Optional Enhancements)

1. **Add password hashing** - Use bcrypt for secure password storage
2. **Add email notifications** - Send hall tickets via email
3. **QR code scanning** - Implement QR code verification page
4. **File upload** - Allow student photo uploads
5. **Reports** - Generate attendance reports
6. **Dashboard analytics** - Add charts and statistics
7. **Mobile responsiveness** - Improve UI for mobile devices

---

## 🎯 Summary

The EXAM Management System is now **fully functional** with:
- ✅ Complete MongoDB integration
- ✅ All database models working
- ✅ Authentication system functional
- ✅ Python wrappers integrated
- ✅ PDF generation working
- ✅ All user roles implemented (COE, Faculty, Student)
- ✅ Complete workflow from scheduling to hall tickets

**Server is running at: http://localhost:5000**

Login and test all features with the provided credentials!
