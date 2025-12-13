const express = require('express');
const { protect, authorize } = require('../middleware/auth');

const router = express.Router();

// All routes are protected and require 'faculty' role
router.use(protect);
router.use(authorize('faculty'));

// @route   GET /api/faculty/dashboard
// @desc    Render Faculty dashboard
// @access  Private (Faculty only)
router.get('/dashboard', async (req, res) => {
    try {
        res.render('faculty/dashboard', {
            user: req.user,
            title: 'Faculty Dashboard'
        });
    } catch (error) {
        console.error('Faculty Dashboard Error:', error);
        res.status(500).send('Server Error');
    }
});

// More routes will be added here

module.exports = router;
