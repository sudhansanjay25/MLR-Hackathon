const mongoose = require('mongoose');

const examScheduleSchema = new mongoose.Schema({
    academicYear: {
        type: String,
        required: true
    },
    examType: {
        type: String,
        enum: ['Internal1', 'Internal2', 'Internal', 'SEM'],
        required: true
    },
    year: {
        type: Number,
        required: true,
        min: 1,
        max: 4
    },
    semester: {
        type: Number,
        required: true,
        min: 1,
        max: 8
    },
    startDate: {
        type: Date,
        required: true
    },
    endDate: {
        type: Date,
        required: true
    },
    session: {
        type: String,
        enum: ['FN', 'AN'],
        default: 'FN'
    },
    facultyIncharge: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }],
    halls: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Hall'
    }],
    timetablePdfPath: {
        type: String
    },
    seatingPdfPaths: {
        studentPdf: String,
        facultyPdf: String
    },
    hallTicketsAuthorized: {
        type: Boolean,
        default: false
    },
    status: {
        type: String,
        enum: ['Draft', 'Scheduled', 'Ongoing', 'Completed', 'Cancelled'],
        default: 'Draft'
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

module.exports = mongoose.model('ExamSchedule', examScheduleSchema);
