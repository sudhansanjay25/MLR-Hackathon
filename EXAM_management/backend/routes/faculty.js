const express = require('express');
const { protect, authorize } = require('../middleware/auth');
const ExamSchedule = require('../models/ExamSchedule');
const ExamTimetable = require('../models/ExamTimetable');
const SeatingAllocation = require('../models/SeatingAllocation');
const Attendance = require('../models/Attendance');

const router = express.Router();

// All routes are protected and require 'faculty' role
router.use(protect);
router.use(authorize('faculty'));

// @route   GET /api/faculty/dashboard
// @desc    Render Faculty dashboard
// @access  Private (Faculty only)
router.get('/dashboard', async (req, res) => {
    try {
        // Get upcoming exams where this faculty is assigned
        const upcomingExams = await ExamSchedule.find({
            facultyIncharge: req.user.id,
            startDate: { $gte: new Date() },
            isActive: true
        })
        .populate('halls', 'hallNumber building')
        .sort({ startDate: 1 })
        .limit(5);
        
        res.render('faculty/dashboard', {
            user: req.user,
            title: 'Faculty Dashboard',
            upcomingExams
        });
    } catch (error) {
        console.error('Faculty Dashboard Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/faculty/my-schedules
// @desc    Get all schedules assigned to this faculty
// @access  Private (Faculty only)
router.get('/my-schedules', async (req, res) => {
    try {
        const schedules = await ExamSchedule.find({
            facultyIncharge: req.user.id,
            isActive: true
        })
        .populate('halls', 'hallNumber building')
        .sort({ startDate: -1 });
        
        res.json({ success: true, schedules });
    } catch (error) {
        console.error('Get Schedules Error:', error);
        res.status(500).json({ success: false, message: 'Error fetching schedules' });
    }
});

// @route   GET /api/faculty/attendance/:scheduleId
// @desc    Get attendance marking page
// @access  Private (Faculty only)
router.get('/attendance/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);
        const timetable = await ExamTimetable.find({ schedule: req.params.scheduleId });
        
        res.render('faculty/mark-attendance', {
            user: req.user,
            title: 'Mark Attendance',
            schedule,
            timetable
        });
    } catch (error) {
        console.error('Attendance Page Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   POST /api/faculty/mark-attendance
// @desc    Mark student attendance
// @access  Private (Faculty only)
router.post('/mark-attendance', async (req, res) => {
    try {
        const { examTimetableId, registerNumber, status } = req.body;
        
        // Find student
        const User = require('../models/User');
        const student = await User.findOne({ registerNumber, role: 'student' });
        
        if (!student) {
            return res.status(404).json({ success: false, message: 'Student not found' });
        }
        
        // Create or update attendance
        const attendance = await Attendance.findOneAndUpdate(
            { examTimetable: examTimetableId, student: student._id },
            {
                registerNumber,
                status,
                verificationMethod: 'manual-entry',
                markedBy: req.user.id,
                markedAt: new Date()
            },
            { upsert: true, new: true }
        );
        
        res.json({ success: true, attendance });
    } catch (error) {
        console.error('Mark Attendance Error:', error);
        res.status(500).json({ success: false, message: 'Error marking attendance' });
    }
});

module.exports = router;
