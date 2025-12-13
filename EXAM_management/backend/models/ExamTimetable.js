const mongoose = require('mongoose');

const examTimetableSchema = new mongoose.Schema({
    schedule: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'ExamSchedule',
        required: true
    },
    subject: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Subject',
        required: true
    },
    subjectCode: {
        type: String,
        required: false
    },
    subjectName: {
        type: String,
        required: false
    },
    date: {
        type: Date,
        required: true
    },
    timeStart: {
        type: String,
        required: true
    },
    timeEnd: {
        type: String,
        required: true
    },
    halls: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Hall'
    }],
    invigilators: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }],
    // For tracking violations from scheduling algorithm
    violations: [{
        type: String
    }]
}, {
    timestamps: true
});

// Index for efficient queries
examTimetableSchema.index({ schedule: 1, date: 1 });
examTimetableSchema.index({ subject: 1 });

module.exports = mongoose.model('ExamTimetable', examTimetableSchema);
