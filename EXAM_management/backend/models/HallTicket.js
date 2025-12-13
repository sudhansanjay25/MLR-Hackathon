const mongoose = require('mongoose');

const hallTicketSchema = new mongoose.Schema({
    student: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    schedule: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'ExamSchedule',
        required: true
    },
    registerNumber: {
        type: String,
        required: true
    },
    qrCodeData: {
        type: String,
        required: true
    },
    pdfPath: {
        type: String
    },
    authorized: {
        type: Boolean,
        default: false
    },
    authorizedAt: {
        type: Date
    },
    authorizedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    downloaded: {
        type: Boolean,
        default: false
    },
    downloadedAt: {
        type: Date
    }
}, {
    timestamps: true
});

// Index for efficient queries
hallTicketSchema.index({ student: 1, schedule: 1 }, { unique: true });
hallTicketSchema.index({ registerNumber: 1, schedule: 1 });

module.exports = mongoose.model('HallTicket', hallTicketSchema);
