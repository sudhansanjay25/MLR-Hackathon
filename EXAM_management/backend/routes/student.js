const express = require('express');
const { protect, authorize } = require('../middleware/auth');
const ExamSchedule = require('../models/ExamSchedule');
const ExamTimetable = require('../models/ExamTimetable');
const SeatingAllocation = require('../models/SeatingAllocation');
const HallTicket = require('../models/HallTicket');
const Attendance = require('../models/Attendance');
const path = require('path');
const fs = require('fs').promises;

const router = express.Router();

// All routes are protected and require 'student' role
router.use(protect);
router.use(authorize('student'));

// @route   GET /api/student/dashboard
// @desc    Render Student dashboard
// @access  Private (Student only)
router.get('/dashboard', async (req, res) => {
    try {
        // Get upcoming exams for student's year
        const upcomingExams = await ExamSchedule.find({
            year: req.user.year,
            startDate: { $gte: new Date() },
            isActive: true
        })
        .sort({ startDate: 1 })
        .limit(5);
        
        // Get hall tickets
        const hallTickets = await HallTicket.find({
            student: req.user.id,
            authorized: true
        })
        .populate('schedule', 'examType academicYear startDate endDate')
        .sort({ createdAt: -1 })
        .limit(5);
        
        res.render('student/dashboard', {
            user: req.user,
            title: 'Student Dashboard',
            upcomingExams,
            hallTickets
        });
    } catch (error) {
        console.error('Student Dashboard Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/student/my-schedule
// @desc    Get student's exam schedule
// @access  Private (Student only)
router.get('/my-schedule', async (req, res) => {
    try {
        const schedules = await ExamSchedule.find({
            year: req.user.year,
            isActive: true
        })
        .populate('halls', 'hallNumber building')
        .sort({ startDate: -1 });
        
        res.json({ success: true, schedules });
    } catch (error) {
        console.error('Get Schedule Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching schedule' });
    }
});

// @route   GET /api/student/timetable/:scheduleId
// @desc    Get exam timetable for a schedule
// @access  Private (Student only)
router.get('/timetable/:scheduleId', async (req, res) => {
    try {
        const timetable = await ExamTimetable.find({ schedule: req.params.scheduleId })
            .populate('subject', 'code name')
            .sort({ date: 1 });
        
        res.json({ success: true, timetable });
    } catch (error) {
        console.error('Get Timetable Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching timetable' });
    }
});

// @route   GET /api/student/seating/:scheduleId
// @desc    Get student's seating allocation
// @access  Private (Student only)
router.get('/seating/:scheduleId', async (req, res) => {
    try {
        const seating = await SeatingAllocation.findOne({
            schedule: req.params.scheduleId,
            student: req.user.id
        })
        .populate('hall', 'hallNumber building floor');
        
        if (!seating) {
            return res.status(404).json({ success: false, message: 'Seating not allocated yet' });
        }
        
        res.json({ success: true, seating });
    } catch (error) {
        console.error('Get Seating Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching seating' });
    }
});

// @route   GET /api/student/hall-ticket/:scheduleId
// @desc    Get hall ticket for a schedule
// @access  Private (Student only)
router.get('/hall-ticket/:scheduleId', async (req, res) => {
    try {
        const hallTicket = await HallTicket.findOne({
            schedule: req.params.scheduleId,
            student: req.user.id
        });
        
        if (!hallTicket) {
            return res.status(404).json({ success: false, message: 'Hall ticket not generated yet' });
        }
        
        if (!hallTicket.authorized) {
            return res.status(403).json({ success: false, message: 'Hall ticket not authorized yet' });
        }
        
        res.json({ success: true, hallTicket });
    } catch (error) {
        console.error('Get Hall Ticket Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching hall ticket' });
    }
});

// @route   GET /api/student/download-hall-ticket/:scheduleId
// @desc    Download hall ticket PDF
// @access  Private (Student only)
router.get('/download-hall-ticket/:scheduleId', async (req, res) => {
    try {
        const hallTicket = await HallTicket.findOne({
            schedule: req.params.scheduleId,
            student: req.user.id
        });
        
        if (!hallTicket || !hallTicket.authorized) {
            return res.status(404).send('Hall ticket not available');
        }
        
        if (!hallTicket.pdfPath) {
            return res.status(404).send('PDF not generated');
        }
        
        const filePath = path.resolve(hallTicket.pdfPath);
        await fs.access(filePath);
        
        // Mark as downloaded
        await HallTicket.findByIdAndUpdate(hallTicket._id, {
            downloaded: true,
            downloadedAt: new Date()
        });
        
        const filename = path.basename(filePath);
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', 'application/pdf');
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('Download Hall Ticket Error:', error);
        res.status(404).send('File not found');
    }
});

// @route   GET /api/student/attendance/:scheduleId
// @desc    Get attendance records for a schedule
// @access  Private (Student only)
router.get('/attendance/:scheduleId', async (req, res) => {
    try {
        const timetable = await ExamTimetable.find({ schedule: req.params.scheduleId });
        const timetableIds = timetable.map(t => t._id);
        
        const attendanceRecords = await Attendance.find({
            examTimetable: { $in: timetableIds },
            student: req.user.id
        })
        .populate('examTimetable', 'date subjectCode subjectName');
        
        res.json({ success: true, attendance: attendanceRecords });
    } catch (error) {
        console.error('Get Attendance Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching attendance' });
    }
});

module.exports = router;
