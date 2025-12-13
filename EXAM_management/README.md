# EXAM Management System

Integrated system for managing exams including scheduling, seating arrangement, and hall ticket generation.

## Features

- **COE Dashboard**: Schedule exams, authorize hall tickets, manage resources
- **Faculty Dashboard**: QR code scanning, attendance marking, view assigned exams
- **Student Dashboard**: View exam schedule, download hall tickets, check attendance
- **Automated Workflows**: Scheduling → Seating → Hall Tickets → Attendance

## Tech Stack

- **Backend**: Node.js, Express.js, MongoDB
- **Frontend**: HTML, CSS, JavaScript, EJS
- **Python Modules**: Scheduling algorithm, Seating arrangement, Hall ticket generation
- **Authentication**: JWT
- **QR Code**: qrcode.js, html5-qrcode

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- MongoDB (v5 or higher)
- Python 3.x (with ht venv)

### Installation

1. Install Node.js dependencies:
```bash
npm install
```

2. Set up Python environment (ht venv should already exist):
```bash
# Activate ht venv
..\ht\Scripts\activate

# Install Python dependencies (if needed)
pip install pandas matplotlib reportlab qrcode
```

3. Configure environment variables:
   - Copy `.env` file and update values if needed
   - Ensure MongoDB is running on localhost:27017

4. Generate mock data:
```bash
npm run seed
```

5. Start the server:
```bash
npm start
# or for development with auto-reload:
npm run dev
```

6. Access the application:
```
http://localhost:5000
```

## Default Login Credentials

### COE
- Email: `coe@mlrit.ac.in`
- Password: `coe123`

### Faculty
- Email: `faculty001@mlrit.ac.in`
- Password: `faculty123`

### Student
- Email: `714025104001@mlrit.ac.in`
- Password: `student123`

## Project Structure

```
EXAM_management/
├── backend/              # Node.js backend
│   ├── config/          # Database configuration
│   ├── models/          # MongoDB schemas
│   ├── routes/          # API routes
│   ├── controllers/     # Business logic
│   ├── middleware/      # Auth & validation
│   ├── utils/           # Helper functions
│   └── uploads/         # Generated files
├── frontend/            # Frontend views
│   ├── public/         # Static files
│   └── views/          # EJS templates
├── modules/            # Python modules
│   ├── exam_scheduling/
│   ├── seating_arrangement/
│   └── hall_ticket_generation/
└── scripts/            # Utility scripts
```

## Workflow

1. **COE** selects resources (faculty & halls) and creates exam schedule
2. **Scheduling Module** generates timetable automatically
3. **Seating Module** allocates students to halls automatically
4. **COE** authorizes hall tickets (SEM exams only)
5. **Students** download hall tickets with QR codes
6. **Faculty** scan QR codes to mark attendance (30-min window)

## API Endpoints

### Authentication
- POST `/api/auth/login`
- POST `/api/auth/logout`

### COE
- GET `/api/coe/resources` - Get available faculty & halls
- POST `/api/coe/schedule` - Create exam schedule
- GET `/api/coe/schedules` - View all schedules
- POST `/api/coe/authorize-halltickets` - Authorize hall tickets

### Faculty
- GET `/api/faculty/assigned-exams` - Get assigned exams
- POST `/api/faculty/scan-qr` - Verify and mark attendance
- POST `/api/faculty/manual-entry` - Manual attendance entry
- GET `/api/faculty/attendance/:examId` - View attendance

### Student
- GET `/api/student/schedule` - View exam schedule
- GET `/api/student/hallticket` - Download hall ticket
- GET `/api/student/attendance` - View attendance status

## License

MIT

---

## ✅ Phase 5 Complete - Hall Ticket Generation

### New Features (December 12, 2025)
- ✅ MongoDB-integrated hall ticket generation
- ✅ QR code generation for verification
- ✅ Single and bulk hall ticket generation
- ✅ ReportLab PDF creation (Windows-compatible)
- ✅ Professional formatting with college header
- ✅ Automatic subject fetching from schedule timetable

### Files Added
- `modules/hall_ticket_wrapper.py` - Hall ticket generator (476 lines)
- `modules/test_hall_ticket.py` - Single generation test
- `modules/test_bulk_hall_tickets.py` - Bulk generation test

### API Endpoints Added
```http
POST /api/coe/generate-hall-ticket
POST /api/coe/generate-bulk-hall-tickets
POST /api/coe/authorize-hall-tickets/:scheduleId (updated)
```

### Test Results
- ✅ Single generation: 1/1 (100%)
- ✅ Bulk generation: 5/5 (100%)
- ✅ PDF format: Professional with QR codes
- ✅ Output: 9-10 KB per PDF

### Documentation
See detailed documentation:
- [PHASE_5_COMPLETE.md](PHASE_5_COMPLETE.md) - Usage guide
- [PHASE_5_TEST_RESULTS.md](PHASE_5_TEST_RESULTS.md) - Test results
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete overview
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture

### Status
**ALL 5 PHASES COMPLETE** - Production Ready ✓

Hall ticket generation is fully integrated and tested. The system can now:
1. Schedule exams with automated timetable
2. Allocate seating with visual PDFs
3. Generate hall tickets with QR codes
4. Track attendance (existing feature)

**Total System Status**: 🎉 PRODUCTION READY
