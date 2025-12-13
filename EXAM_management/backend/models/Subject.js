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
    department: { type: mongoose.Schema.Types.ObjectId, ref: 'Department' },
    year: { type: Number, required: true, min: 1, max: 4 },
    semester: { type: Number, required: true, min: 1, max: 8 },
    type: { type: String, enum: ['Theory', 'Lab', 'Project'], default: 'Theory' },
    credits: { type: Number, required: true, default: 3 },
    faculty: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    isActive: { type: Boolean, default: true }
}, {
    timestamps: true
});

module.exports = mongoose.model('Subject', subjectSchema);
