const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load env vars
dotenv.config({ path: path.join(__dirname, '.env') });

// Import models
const Student = require('./backend/models/Student');
const Hall = require('./backend/models/Hall');

// Connect to MongoDB
const testQuery = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        console.log('✓ MongoDB Connected\n');
        
        // Test student count for Year 1, Semester 1
        console.log('Testing Student Count Query:');
        console.log('============================');
        const year1sem1Count = await Student.countDocuments({
            year: 1,
            semester: 1,
            isActive: true
        });
        console.log(`Year 1, Semester 1: ${year1sem1Count} students`);
        
        // Check all year/semester combinations
        for (let year = 1; year <= 4; year++) {
            for (let sem = 1; sem <= 2; sem++) {
                const count = await Student.countDocuments({
                    year: year,
                    semester: sem,
                    isActive: true
                });
                console.log(`Year ${year}, Semester ${sem}: ${count} students`);
            }
        }
        
        console.log('\nTesting Hall Configuration:');
        console.log('============================');
        const halls = await Hall.find({ isActive: true })
            .select('hallNumber capacity examCapacity columns');
        halls.forEach(hall => {
            console.log(`${hall.hallNumber}: ${hall.capacity} benches, ${hall.columns || 'undefined'} columns`);
        });
        
        mongoose.connection.close();
        console.log('\n✓ Test completed');
    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
};

testQuery();
