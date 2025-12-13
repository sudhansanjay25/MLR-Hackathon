const express = require('express');
const { protect, authorize } = require('../middleware/auth');
const { runScheduling, runSeatingArrangement, generateTimetablePDF, generateSeatingPDFs } = require('../utils/pythonRunner');
// Scrapped DB dependence for scheduling/seating; adapt to module outputs
// Keep core Python modules intact; align responses to frontend expectations
const path = require('path');
const fs = require('fs').promises;

const router = express.Router();

// All routes are protected and require 'coe' role
router.use(protect);
router.use(authorize('coe'));

// @route   GET /api/coe/dashboard
// @desc    Render COE dashboard
// @access  Private (COE only)
router.get('/dashboard', async (req, res) => {
    try {
        res.render('coe/dashboard', {
            user: req.user,
            title: 'COE Dashboard'
        });
    } catch (error) {
        console.error('COE Dashboard Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/coe/schedule-exam
// @desc    Render schedule exam page
// @access  Private (COE only)
router.get('/schedule-exam', async (req, res) => {
    try {
        res.render('coe/schedule-exam', {
            user: req.user,
            title: 'Schedule Exam'
        });
    } catch (error) {
        console.error('Schedule Exam Page Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/coe/view-schedules
// @desc    View all exam schedules
// @access  Private (COE only)
router.get('/view-schedules', async (req, res) => {
    try {
        // No DB: provide a lightweight view using generated uploads if present
        res.render('coe/view-schedules', {
            user: req.user,
            title: 'View Schedules',
            schedules: []
        });
    } catch (error) {
        console.error('View Schedules Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/coe/faculty
// @desc    Get all faculty for selection
// @access  Private (COE only)
router.get('/faculty', async (req, res) => {
    try {
        // Without DB, return empty list or integrate a static list if available
        res.json([]);
    } catch (error) {
        console.error('Get Faculty Error:', error);
        res.status(500).json({ message: 'Error fetching faculty' });
    }
});

// @route   GET /api/coe/halls
// @desc    Get all halls for selection
// @access  Private (COE only)
router.get('/halls', async (req, res) => {
    try {
        // Without DB, return empty list; frontend should provide selections
        res.json([]);
    } catch (error) {
        console.error('Get Halls Error:', error);
        res.status(500).json({ message: 'Error fetching halls' });
    }
});

// @route   GET /api/coe/student-count
// @desc    Get student count for a specific year
// @access  Private (COE only)
router.get('/student-count', async (req, res) => {
    try {
        const { year } = req.query;
        if (!year) return res.status(400).json({ message: 'Year parameter is required' });
        // Without DB, let frontend handle counts; return 0 as placeholder
        res.json({ count: 0, year: parseInt(year) });
    } catch (error) {
        console.error('Get Student Count Error:', error);
        res.status(500).json({ message: 'Error fetching student count' });
    }
});

// @route   POST /api/coe/schedule-exam
// @desc    Generate exam schedule and seating arrangement
// @access  Private (COE only)
router.post('/schedule-exam', async (req, res) => {
    try {
        const {
            academicYear,
            examType,
            year,
            semester,
            session,
            startDate,
            endDate,
            holidays,
            selectedFaculty,
            selectedHalls
        } = req.body;

        // Validation
        if (!academicYear || !examType || !year || !semester || !startDate || !endDate) {
            return res.status(400).json({ message: 'Missing required fields (academicYear, examType, year, semester, startDate, endDate required)' });
        }

        if (selectedFaculty.length === 0 || selectedHalls.length === 0) {
            return res.status(400).json({ message: 'Must select at least one faculty and one hall' });
        }

        // No DB: directly run scheduling and seating via Python wrappers

        // Step 1: Run Python scheduling script
        console.log('Running scheduling algorithm...');
        const schedulingParams = {
            year,
            semester,
            examType,
            session: session || null,
            startDate,
            endDate,
            holidays: holidays || [],
            scheduleId: `${year}-${semester}-${examType}-${Date.now()}`
        };

        const schedulingResult = await runScheduling(schedulingParams);
        
        console.log('Scheduling result:', JSON.stringify(schedulingResult, null, 2));
        
        if (!schedulingResult.success) {
            throw new Error('Scheduling failed: ' + schedulingResult.message);
        }

        console.log(`Scheduling completed successfully - ${schedulingResult.timetable.length} timetable entries generated`);

        // Step 2: Prepare timetable payload for frontend (no DB)
        const assignedHalls = selectedHalls;
        const assignedFaculty = selectedFaculty.slice(0, 2);
        const timetableEntries = schedulingResult.timetable.map(entry => ({
            subjectCode: entry.subjectCode,
            subjectName: entry.subjectName || entry.subjectCode,
            date: entry.date,
            timeStart: entry.timeStart,
            timeEnd: entry.timeEnd,
            halls: assignedHalls,
            invigilators: assignedFaculty
        }));

        // Step 3: Run seating arrangement
        console.log('Running seating arrangement...');
        const seatingParams = {
            year,
            examType,
            session: session || null,
            halls: selectedHalls,
            scheduleId: schedulingParams.scheduleId
        };

        const seatingResult = await runSeatingArrangement(seatingParams);
        
        if (!seatingResult.success) {
            console.warn('Seating arrangement warning:', seatingResult.message);
        } else {
            console.log('Seating arrangement completed successfully');

            // Collect seating info for response
            const seatingInfo = {
                studentPdf: seatingResult.data?.studentPdfPath,
                facultyPdf: seatingResult.data?.facultyPdfPath,
                totalStudents: seatingResult.data?.totalStudents,
                hallsUsed: seatingResult.data?.hallsUsed,
                allocationsCount: seatingResult.allocations?.length || 0
            };
        }

        // Step 4: Generate PDFs
        console.log('Generating PDFs...');
        try {
            const timetablePdfResult = await generateTimetablePDF(schedulingParams.scheduleId);
            const seatingPdfsResult = await generateSeatingPDFs(schedulingParams.scheduleId);
            if (timetablePdfResult.success) {
                console.log('Timetable PDF generated:', timetablePdfResult.filename);
            }
            if (seatingPdfsResult.success) {
                console.log('Seating PDFs generated:', seatingPdfsResult.studentPdf.filename, seatingPdfsResult.facultyPdf.filename);
            }
        } catch (pdfError) {
            console.error('PDF Generation Error:', pdfError);
            // Don't fail the whole request if PDF generation fails
        }

        res.status(201).json({
            success: true,
            message: 'Schedule and seating generated successfully',
            scheduleId: schedulingParams.scheduleId,
            timetable: timetableEntries
        });

    } catch (error) {
        console.error('Schedule Exam Error:', error);
        res.status(500).json({ 
            success: false,
            message: error.message || 'Error generating schedule' 
        });
    }
});

// @route   GET /api/coe/view-schedule/:id
// @desc    View specific exam schedule
// @access  Private (COE only)
router.get('/view-schedule/:id', async (req, res) => {
    try {
        // With scrapped DB, render with minimal context
        res.render('coe/view-schedule', {
            user: req.user,
            title: 'View Schedule',
            schedule: { _id: req.params.id },
            timetable: []
        });
    } catch (error) {
        console.error('View Schedule Error:', error);
        res.status(500).send('Server Error');
    }
});

// @route   GET /api/coe/download-pdf
// @desc    Download PDF file
// @access  Private (COE only)
router.get('/download-pdf', async (req, res) => {
    try {
        const { path: filePath } = req.query;
        
        if (!filePath) {
            return res.status(400).send('File path required');
        }

        // Security: Ensure file is within allowed directories
        const allowedDirs = [
            path.join(__dirname, '../../modules/exam_scheduling'),
            path.join(__dirname, '../../modules/seating_arrangement'),
            path.join(__dirname, '../../uploads')
        ];

        const absolutePath = path.resolve(filePath);
        const isAllowed = allowedDirs.some(dir => absolutePath.startsWith(path.resolve(dir)));

        if (!isAllowed) {
            return res.status(403).send('Access denied');
        }

        // Check if file exists
        await fs.access(absolutePath);

        res.download(absolutePath);
    } catch (error) {
        console.error('Download PDF Error:', error);
        res.status(404).send('File not found');
    }
});

// @route   GET /api/coe/download-timetable/:scheduleId
// @desc    Download timetable PDF for a schedule
// @access  Private (COE only)
router.get('/download-timetable/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);
        
        if (!schedule) {
            return res.status(404).json({ message: 'Schedule not found' });
        }

        if (!schedule.timetablePdfPath) {
            return res.status(404).json({ message: 'Timetable PDF not generated yet' });
        }

        const filePath = path.resolve(schedule.timetablePdfPath);
        
        // Security check
        const allowedDir = path.resolve('uploads/timetables');
        if (!filePath.startsWith(allowedDir)) {
            return res.status(403).json({ message: 'Access denied' });
        }

        await fs.access(filePath);
        
        // Set headers to trigger browser download
        const filename = path.basename(filePath);
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', 'application/pdf');
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('Download Timetable Error:', error);
        res.status(404).json({ message: 'File not found' });
    }
});

// @route   GET /api/coe/download-seating-student/:scheduleId
// @desc    Download student seating arrangement PDF
// @access  Private (COE only)
router.get('/download-seating-student/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);
        
        if (!schedule) {
            return res.status(404).json({ message: 'Schedule not found' });
        }

        if (!schedule.seatingPdfPaths?.studentPdf) {
            return res.status(404).json({ message: 'Student seating PDF not generated yet' });
        }

        const filePath = path.resolve(schedule.seatingPdfPaths.studentPdf);
        
        // Security check
        const allowedDir = path.resolve('uploads/seating');
        if (!filePath.startsWith(allowedDir)) {
            return res.status(403).json({ message: 'Access denied' });
        }

        await fs.access(filePath);
        
        // Set headers to trigger browser download
        const filename = path.basename(filePath);
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', 'application/pdf');
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('Download Student Seating Error:', error);
        res.status(404).json({ message: 'File not found' });
    }
});

// @route   GET /api/coe/download-seating-faculty/:scheduleId
// @desc    Download faculty seating arrangement PDF (duty roster)
// @access  Private (COE only)
router.get('/download-seating-faculty/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);
        
        if (!schedule) {
            return res.status(404).json({ message: 'Schedule not found' });
        }

        if (!schedule.seatingPdfPaths?.facultyPdf) {
            return res.status(404).json({ message: 'Faculty duty roster PDF not generated yet' });
        }

        const filePath = path.resolve(schedule.seatingPdfPaths.facultyPdf);
        
        // Security check
        const allowedDir = path.resolve('uploads/seating');
        if (!filePath.startsWith(allowedDir)) {
            return res.status(403).json({ message: 'Access denied' });
        }

        await fs.access(filePath);
        
        // Set headers to trigger browser download
        const filename = path.basename(filePath);
        res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
        res.setHeader('Content-Type', 'application/pdf');
        res.download(filePath, filename);
        
    } catch (error) {
        console.error('Download Faculty Seating Error:', error);
        res.status(404).json({ message: 'File not found' });
    }
});

// @route   DELETE /api/coe/schedule/:scheduleId
// @desc    Delete an exam schedule and all related data
// @access  Private (COE only)
router.delete('/schedule/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);

        if (!schedule) {
            return res.status(404).json({ message: 'Schedule not found' });
        }

        // Delete related timetable entries
        await ExamTimetable.deleteMany({ schedule: schedule._id });

        // Delete related seating allocations
        await SeatingAllocation.deleteMany({ schedule: schedule._id });

        // Delete PDF files if they exist
        const fs = require('fs').promises;
        
        if (schedule.timetablePdfPath) {
            try {
                await fs.unlink(path.resolve(schedule.timetablePdfPath));
            } catch (err) {
                console.warn('Could not delete timetable PDF:', err.message);
            }
        }

        if (schedule.seatingPdfPaths?.studentPdf) {
            try {
                await fs.unlink(path.resolve(schedule.seatingPdfPaths.studentPdf));
            } catch (err) {
                console.warn('Could not delete student PDF:', err.message);
            }
        }

        if (schedule.seatingPdfPaths?.facultyPdf) {
            try {
                await fs.unlink(path.resolve(schedule.seatingPdfPaths.facultyPdf));
            } catch (err) {
                console.warn('Could not delete faculty PDF:', err.message);
            }
        }

        // Delete the schedule
        await ExamSchedule.findByIdAndDelete(schedule._id);

        res.json({
            success: true,
            message: 'Schedule deleted successfully'
        });
    } catch (error) {
        console.error('Delete Schedule Error:', error);
        res.status(500).json({ message: 'Error deleting schedule' });
    }
});

// @route   POST /api/coe/authorize-hall-tickets/:scheduleId
// @desc    Authorize hall ticket generation for SEM exams
// @access  Private (COE only)
router.post('/authorize-hall-tickets/:scheduleId', async (req, res) => {
    try {
        const schedule = await ExamSchedule.findById(req.params.scheduleId);

        if (!schedule) {
            return res.status(404).json({ message: 'Schedule not found' });
        }

        if (schedule.examType !== 'SEM') {
            return res.status(400).json({ message: 'Hall tickets only for SEM exams' });
        }

        schedule.hallTicketsAuthorized = true;
        schedule.hallTicketsAuthorizedAt = new Date();
        schedule.hallTicketsAuthorizedBy = req.user._id;
        await schedule.save();

        // Trigger hall ticket generation for all students
        const { generateBulkHallTickets } = require('../utils/pythonRunner');
        
        try {
            const hallTicketsResult = await generateBulkHallTickets(
                scheduleId, 
                schedule.year
            );
            
            if (hallTicketsResult.success) {
                res.json({
                    success: true,
                    message: 'Hall tickets authorized and generated successfully',
                    generated: hallTicketsResult.successful,
                    total: hallTicketsResult.total,
                    failed: hallTicketsResult.failed
                });
            } else {
                res.json({
                    success: false,
                    message: 'Hall tickets authorized but generation failed',
                    error: hallTicketsResult.error
                });
            }
        } catch (generationError) {
            console.error('Hall Ticket Generation Error:', generationError);
            // Authorization was successful, but generation failed
            res.json({
                success: true,
                message: 'Hall tickets authorized, but generation encountered errors',
                error: generationError.message
            });
        }
    } catch (error) {
        console.error('Authorize Hall Tickets Error:', error);
        res.status(500).json({ message: 'Error authorizing hall tickets' });
    }
});

// @route   POST /api/coe/generate-hall-ticket
// @desc    Generate hall ticket for a single student
// @access  Private (COE only)
router.post('/generate-hall-ticket', async (req, res) => {
    try {
        const { scheduleId, registerNumber } = req.body;

        if (!scheduleId || !registerNumber) {
            return res.status(400).json({
                success: false,
                message: 'Schedule ID and register number are required'
            });
        }

        // Check if schedule exists
        const schedule = await ExamSchedule.findById(scheduleId);
        if (!schedule) {
            return res.status(404).json({
                success: false,
                message: 'Schedule not found'
            });
        }

        // Generate hall ticket
        const { generateSingleHallTicket } = require('../utils/pythonRunner');
        const result = await generateSingleHallTicket(scheduleId, registerNumber);

        if (result.success) {
            res.json({
                success: true,
                message: 'Hall ticket generated successfully',
                pdfPath: result.pdfPath,
                registerNumber: result.registerNumber
            });
        } else {
            res.status(500).json({
                success: false,
                message: 'Failed to generate hall ticket',
                error: result.error
            });
        }
    } catch (error) {
        console.error('Generate Hall Ticket Error:', error);
        res.status(500).json({
            success: false,
            message: 'Error generating hall ticket',
            error: error.message
        });
    }
});

// @route   POST /api/coe/generate-bulk-hall-tickets
// @desc    Generate hall tickets for all students in a year
// @access  Private (COE only)
router.post('/generate-bulk-hall-tickets', async (req, res) => {
    try {
        const { scheduleId, year } = req.body;

        if (!scheduleId) {
            return res.status(400).json({
                success: false,
                message: 'Schedule ID is required'
            });
        }

        // Check if schedule exists
        const schedule = await ExamSchedule.findById(scheduleId);
        if (!schedule) {
            return res.status(404).json({
                success: false,
                message: 'Schedule not found'
            });
        }

        // Generate bulk hall tickets
        const { generateBulkHallTickets } = require('../utils/pythonRunner');
        const result = await generateBulkHallTickets(scheduleId, year || schedule.year);

        if (result.success) {
            res.json({
                success: true,
                message: 'Hall tickets generated successfully',
                generated: result.successful,
                total: result.total,
                failed: result.failed,
                hallTickets: result.generated
            });
        } else {
            res.status(500).json({
                success: false,
                message: 'Failed to generate hall tickets',
                error: result.error
            });
        }
    } catch (error) {
        console.error('Generate Bulk Hall Tickets Error:', error);
        res.status(500).json({
            success: false,
            message: 'Error generating hall tickets',
            error: error.message
        });
    }
});

module.exports = router;
