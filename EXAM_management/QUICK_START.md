# Quick Start Guide

## ⚡ Start the System (Every Time)

### 1. Start MongoDB
Make sure MongoDB is running on your system.

### 2. Start the Server
```powershell
cd c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\EXAM_management\backend
node server.js
```

### 3. Open Browser
Navigate to: **http://localhost:5000**

---

## 🔑 Test Login Credentials

### COE Dashboard
```
Email: coe@mlrit.ac.in
Password: coe123
```

### Faculty Dashboard
```
Email: faculty001@mlrit.ac.in
Password: faculty123
```

### Student Dashboard
```
Email: 714025104001@mlrit.ac.in
Password: student123
```

---

## 🧪 Test the Complete Workflow

### Step 1: Login as COE
1. Go to http://localhost:5000
2. Login with COE credentials
3. Should redirect to COE Dashboard

### Step 2: Create an Exam Schedule
1. Click "Schedule Exam"
2. Fill in the form:
   - Academic Year: `2024-2025`
   - Exam Type: `Internal`
   - Year: `1`
   - Semester: `1`
   - Start Date: Select a future date
   - End Date: Select a date 1 week later
   - Select at least one faculty
   - Select at least one hall
3. Click "Create Schedule"
4. Wait for scheduling, seating, and PDF generation to complete

### Step 3: View the Schedule
1. Go to "View Schedules"
2. Click on the newly created schedule
3. You should see:
   - Exam details
   - Timetable
   - Download buttons for PDFs

### Step 4: Authorize Hall Tickets
1. From the schedule view
2. Click "Authorize Hall Tickets"
3. Wait for hall ticket generation

### Step 5: Login as Student
1. Logout from COE
2. Login with student credentials
3. Should see:
   - Upcoming exams on dashboard
   - Hall ticket download option (if authorized)

### Step 6: Login as Faculty
1. Logout from Student
2. Login with faculty credentials
3. Should see:
   - Assigned exams on dashboard
   - Duty roster information

---

## 📊 Database Info

### Collections Created:
- users (6 users: 1 COE, 2 Faculty, 60 Students)
- departments (4 departments: CSE, ECE, MECH, CIVIL)
- halls (4 halls: A-101, A-102, B-201, B-202)
- subjects (10 subjects across 4 years)
- students (60 students across 4 years)

### Student Distribution:
- Year 1: 15 students (Register numbers: 724025100001-724025100015)
- Year 2: 15 students (Register numbers: 723025100001-723025100015)
- Year 3: 15 students (Register numbers: 722025100001-722025100015)
- Year 4: 15 students (Register numbers: 714025100001-714025100015)

---

## 🔄 If You Need to Reset

### Reset Database
```powershell
cd c:\Users\Lenovo\Desktop\Project\One-Stop-Hackathon\EXAM_management
node seed.js
```

This will:
1. Clear all existing data
2. Create fresh test data
3. Reset to initial state

---

## ⚙️ Troubleshooting

### Server won't start - Port in use
```powershell
# Kill all node processes
Get-Process node | Stop-Process -Force
# Then restart the server
```

### Can't login
- Make sure you ran `node seed.js`
- Check if MongoDB is running
- Verify credentials match exactly (case-sensitive)

### MongoDB not connecting
- Ensure MongoDB service is running
- Check connection string in `.env`: `mongodb://localhost:27017/exam_management`
- Try: `mongo` in command line to verify MongoDB is accessible

---

## 📝 Feature Checklist

- ✅ User Authentication (COE, Faculty, Student)
- ✅ COE Dashboard
- ✅ Schedule Exam Creation
- ✅ Automatic Timetable Generation
- ✅ Automatic Seating Arrangement
- ✅ PDF Generation (Timetable, Seating, Hall Tickets)
- ✅ Hall Ticket Authorization
- ✅ Faculty Dashboard
- ✅ Student Dashboard
- ✅ Download Hall Tickets
- ✅ Attendance Tracking
- ✅ MongoDB Integration
- ✅ Python Module Integration

---

## 🎉 Success Indicators

When everything is working:
1. Server starts with no errors
2. You can login with all 3 roles
3. COE can create schedules successfully
4. PDFs are generated in `outputs/` folders
5. Students can see and download hall tickets
6. Faculty can see their assignments

**Current Status: ALL SYSTEMS OPERATIONAL ✅**
