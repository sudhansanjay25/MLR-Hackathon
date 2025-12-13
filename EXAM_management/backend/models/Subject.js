const mongoose = require('mongoose');

const subjectSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true
    },
    code: {
        type: String,
        required: true,
        uppercase: true,
        trim: true
    },
    department: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Department',
        required: function() {
            return this.type !== 'common';
        }
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
    type: {
        type: String,
        enum: ['major', 'non-major', 'common'],
        default: 'major'
    },
    credits: {
        type: Number,
        required: true,
        default: 3
    },
    faculty: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    },
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true
});

// Compound index for efficient queries
subjectSchema.index({ year: 1, semester: 1, department: 1 });
subjectSchema.index({ code: 1 }, { unique: true });

module.exports = mongoose.model('Subject', subjectSchema);
