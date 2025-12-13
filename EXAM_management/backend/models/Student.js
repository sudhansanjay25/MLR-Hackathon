const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema({
    registerNumber: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        index: true
    },
    name: {
        type: String,
        required: true,
        trim: true
    },
    department: {
        type: String,
        required: true,
        trim: true,
        index: true
    },
    yearOfStudy: {
        type: Number,
        required: true,
        min: 1,
        max: 4,
        index: true
    },
    semester: {
        type: Number,
        min: 1,
        max: 8
    },
    email: {
        type: String,
        lowercase: true,
        trim: true
    },
    phone: {
        type: String,
        trim: true
    },
    photoUrl: {
        type: String,
        default: '/images/default-avatar.png'
    },
    isActive: {
        type: Boolean,
        default: true,
        index: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
}, {
    collection: 'students',
    timestamps: true
});

// Index for common queries
studentSchema.index({ yearOfStudy: 1, isActive: 1 });
studentSchema.index({ department: 1, yearOfStudy: 1 });

module.exports = mongoose.model('Student', studentSchema);
