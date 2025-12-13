const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load env vars
dotenv.config({ path: path.join(__dirname, '.env') });

async function fixIndexes() {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        console.log('✓ MongoDB Connected');
        
        const SeatingAllocation = mongoose.connection.collection('seatingallocations');
        
        // Get all existing indexes
        const indexes = await SeatingAllocation.indexes();
        console.log('\nExisting indexes:');
        indexes.forEach(idx => {
            console.log(`  - ${idx.name}: ${JSON.stringify(idx.key)}`);
        });
        
        // Drop the problematic index with examTimetable
        console.log('\nDropping old indexes...');
        try {
            await SeatingAllocation.dropIndex('schedule_1_examTimetable_1_hall_1_seatNumber_1');
            console.log('✓ Dropped schedule_1_examTimetable_1_hall_1_seatNumber_1');
        } catch (err) {
            if (err.codeName === 'IndexNotFound') {
                console.log('  Index already dropped or not found');
            } else {
                console.log('  Error dropping index:', err.message);
            }
        }
        
        // Ensure correct indexes exist
        console.log('\nVerifying correct indexes exist...');
        try {
            await SeatingAllocation.createIndex(
                { schedule: 1, hall: 1, seatNumber: 1 },
                { unique: true, name: 'schedule_hall_seat_unique' }
            );
            console.log('✓ Created unique index: schedule_hall_seat_unique');
        } catch (err) {
            if (err.codeName === 'IndexOptionsConflict') {
                console.log('✓ Unique index already exists: schedule_1_hall_1_seatNumber_1');
            } else {
                throw err;
            }
        }
        
        try {
            await SeatingAllocation.createIndex(
                { student: 1, schedule: 1 },
                { name: 'student_schedule_index' }
            );
            console.log('✓ Created index: student_schedule_index');
        } catch (err) {
            if (err.codeName === 'IndexOptionsConflict') {
                console.log('✓ Index already exists: student_1_schedule_1');
            } else {
                throw err;
            }
        }
        
        // Show final indexes
        const finalIndexes = await SeatingAllocation.indexes();
        console.log('\nFinal indexes:');
        finalIndexes.forEach(idx => {
            console.log(`  - ${idx.name}: ${JSON.stringify(idx.key)}`);
        });
        
        mongoose.connection.close();
        console.log('\n✅ Indexes fixed successfully!');
    } catch (error) {
        console.error('❌ Error:', error);
        process.exit(1);
    }
}

fixIndexes();
