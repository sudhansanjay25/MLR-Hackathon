const mongoose = require('mongoose');

const attendanceSchema = new mongoose.Schema({
    examTimetable: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'ExamTimetable',
        required: true
    },
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    registerNumber: {
        type: String,
        required: true
    },
    status: {
        type: String,
        enum: ['present', 'absent', 'late'],
        default: 'present'
    },
    verificationMethod: {
        type: String,
        enum: ['qr-scan', 'manual-entry'],
        required: true
    },
    markedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    markedAt: {
        type: Date,
        default: Date.now
    },
    // For COE modifications
    modifiedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    modifiedAt: {
        type: Date
    },
    modificationReason: {
        type: String
    }
}, {
    timestamps: true
});

// Compound index for uniqueness
attendanceSchema.index({ examTimetable: 1, student: 1 }, { unique: true });
attendanceSchema.index({ registerNumber: 1, examTimetable: 1 });

module.exports = mongoose.model('Attendance', attendanceSchema);
