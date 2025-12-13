const mongoose = require('mongoose');

const seatingAllocationSchema = new mongoose.Schema({
    schedule: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'ExamSchedule',
        required: true
    },
    examTimetable: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'ExamTimetable',
        required: true
    },
    hall: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Hall',
        required: true
    },
    hallNumber: {
        type: String,
        required: true
    },
    seatNumber: {
        type: Number,
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
    studentName: {
        type: String,
        required: false
    },
    department: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Department'
    },
    // For internal exams (2 students per bench)
    isLeftSeat: {
        type: Boolean,
        default: null
    },
    pdfGenerated: {
        type: Boolean,
        default: false
    },
    studentPdfPath: {
        type: String
    },
    facultyPdfPath: {
        type: String
    }
}, {
    timestamps: true
});

// Compound index for uniqueness
seatingAllocationSchema.index({ schedule: 1, examTimetable: 1, hall: 1, seatNumber: 1 }, { unique: true });
seatingAllocationSchema.index({ student: 1, schedule: 1 });

module.exports = mongoose.model('SeatingAllocation', seatingAllocationSchema);
