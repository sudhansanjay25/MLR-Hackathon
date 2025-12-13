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
    columns: {
        type: Number,
        required: true,
        min: 1
    },
    building: {
        type: String,
        default: 'Main Building'
    },
    floor: {
        type: Number,
        default: 1
    },
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

module.exports = mongoose.model('Hall', hallSchema);
