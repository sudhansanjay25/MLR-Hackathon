const express = require('express');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// All routes are protected and require 'student' role
router.use(protect);
router.use(authorize('student'));

// @route   GET /api/student/dashboard
// @desc    Render Student dashboard
// @access  Private (Student only)
router.get('/dashboard', async (req, res) => {
    try {
        res.render('student/dashboard', {
            user: req.user,
            title: 'Student Dashboard'
        });
    } catch (error) {
        console.error('Student Dashboard Error:', error);
        res.status(500).send('Server Error');
    }
});

// More routes will be added here

module.exports = router;
