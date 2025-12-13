const mongoose = require('mongoose');

const examScheduleSchema = new mongoose.Schema({
    academicYear: {
        type: String,
        required: true
    },
    semester: {
        type: Number,
        required: true,
        min: 1,
        max: 2
    },
    examType: {
        type: String,
        enum: ['Internal1', 'Internal2', 'SEM'],
        required: true
    },
    session: {
        type: String,
        enum: ['FN', 'AN', 'Morning'],
        default: function() {
            return this.examType.startsWith('Internal') ? 'Morning' : 'FN';
        }
    },
    year: {
        type: Number,
        required: true,
        min: 1,
        max: 4
    },
    startDate: {
        type: Date,
        required: true
    },
    endDate: {
        type: Date,
        required: true
    },
    holidays: [{
        type: Date
    }],
    // Selected resources by COE
    selectedFaculty: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }],
    selectedHalls: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Hall'
    }],
    status: {
        type: String,
        enum: ['draft', 'scheduled', 'in-progress', 'completed'],
        default: 'draft'
    },
    createdBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    hallTicketsAuthorized: {
        type: Boolean,
        default: false
    },
    hallTicketsAuthorizedAt: {
        type: Date
    },
    hallTicketsAuthorizedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }
}, {
    timestamps: true
});

// Index for efficient queries
examScheduleSchema.index({ year: 1, semester: 1, examType: 1 });
examScheduleSchema.index({ status: 1 });

module.exports = mongoose.model('ExamSchedule', examScheduleSchema);
