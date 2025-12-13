const mongoose = require('mongoose');

const hallSchema = new mongoose.Schema({
    hallNumber: {
        type: String,
        required: true,
        unique: true,
        trim: true
    },
    capacity: {
        type: Number,
        required: true,
        min: 1
    },
    examCapacity: {
        type: Number,
        min: 1
    },
    columns: {
        type: Number,
        default: 6
    },
    building: {
        type: String,
        default: 'Main Building'
    },
    floor: {
        type: Number,
        default: 1
    },
    facilities: [{
        type: String
    }],
    isActive: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: true,
    toJSON: { virtuals: true },
    toObject: { virtuals: true }
});

// Virtual for hallName (for backward compatibility)
hallSchema.virtual('hallName').get(function() {
    return this.hallNumber;
});

// Pre-save hook to set examCapacity if not provided
hallSchema.pre('save', function(next) {
    if (!this.examCapacity) {
        this.examCapacity = Math.floor(this.capacity / 2);
    }
    next();
});

module.exports = mongoose.model('Hall', hallSchema);
