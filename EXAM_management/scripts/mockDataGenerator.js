const mongoose = require('mongoose');
require('dotenv').config();
const connectDB = require('../backend/config/db');

// Import models
const User = require('../backend/models/User');
const Department = require('../backend/models/Department');
const Subject = require('../backend/models/Subject');
const Hall = require('../backend/models/Hall');

// Department data
const departments = [
    { name: 'Computer Science and Engineering', code: 'CSE' },
    { name: 'Electronics and Communication Engineering', code: 'ECE' },
    { name: 'Electrical and Electronics Engineering', code: 'EEE' },
    { name: 'Mechanical Engineering', code: 'MECH' },
    { name: 'Civil Engineering', code: 'CIVIL' }
];

// Halls data (30 halls)
const hallsData = Array.from({ length: 30 }, (_, i) => ({
    hallNumber: `Hall ${i + 1}`,
    capacity: i < 10 ? 60 : (i < 20 ? 72 : 84),
    columns: i < 10 ? 4 : (i < 20 ? 6 : 6),
    building: i < 15 ? 'Main Building' : 'New Block',
    floor: Math.floor(i / 10) + 1
}));

// Generate mock data
async function generateMockData() {
    try {
        await connectDB();
        
        console.log('\n' + '='.repeat(60));
        console.log('GENERATING MOCK DATA');
        console.log('='.repeat(60) + '\n');

        // Clear existing data
        console.log('Clearing existing data...');
        await User.deleteMany({});
        await Department.deleteMany({});
        await Subject.deleteMany({});
        await Hall.deleteMany({});
        console.log('✓ Cleared existing data\n');

        // Insert departments
        console.log('Creating departments...');
        const createdDepts = await Department.insertMany(departments);
        console.log(`✓ Created ${createdDepts.length} departments\n`);

        const deptMap = {};
        createdDepts.forEach(dept => {
            deptMap[dept.code] = dept._id;
        });

        // Insert halls
        console.log('Creating halls...');
        const createdHalls = await Hall.insertMany(hallsData);
        console.log(`✓ Created ${createdHalls.length} halls\n`);

        // Create COE user
        console.log('Creating COE account...');
        const coe = await User.create({
            name: 'Dr. Controller of Examinations',
            email: 'coe@mlrit.ac.in',
            password: 'coe123',
            role: 'coe',
            isActive: true
        });
        console.log(`✓ Created COE: ${coe.email} / coe123\n`);

        // Create faculty (60 faculty - 12 per department)
        console.log('Creating faculty...');
        const faculty = [];
        let facultyCount = 1;
        
        for (const dept of createdDepts) {
            for (let i = 0; i < 12; i++) {
                faculty.push({
                    name: `Faculty ${facultyCount}`,
                    email: `faculty${String(facultyCount).padStart(3, '0')}@mlrit.ac.in`,
                    password: 'faculty123',
                    role: 'faculty',
                    employeeId: `EMP${String(facultyCount).padStart(3, '0')}`,
                    department: dept._id,
                    phone: `9${String(facultyCount + 1000000000)}`,
                    isActive: true
                });
                facultyCount++;
            }
        }
        
        const createdFaculty = await User.insertMany(faculty);
        console.log(`✓ Created ${createdFaculty.length} faculty\n`);

        // Create students (75 per dept per year = 1500 students total)
        console.log('Creating students...');
        const students = [];
        let studentIdCounter = 1;

        const deptCodes = { 'CSE': '10', 'ECE': '11', 'EEE': '12', 'MECH': '13', 'CIVIL': '14' };
        
        for (const dept of createdDepts) {
            const deptCode = deptCodes[dept.code];
            
            for (let year = 1; year <= 4; year++) {
                for (let i = 1; i <= 75; i++) {
                    const registerNumber = `71402${deptCode}${year}${String(i).padStart(3, '0')}`;
                    students.push({
                        name: `Student ${dept.code} Y${year} ${i}`,
                        email: `${registerNumber}@mlrit.ac.in`,
                        password: 'student123',
                        role: 'student',
                        registerNumber: registerNumber,
                        department: dept._id,
                        year: year,
                        semester: year * 2,
                        photoUrl: '/images/default-avatar.png',
                        isActive: true
                    });
                    studentIdCounter++;
                }
            }
        }
        
        const createdStudents = await User.insertMany(students);
        console.log(`✓ Created ${createdStudents.length} students\n`);

        // Create subjects
        console.log('Creating subjects...');
        const subjects = [];
        let subjectCount = 1;

        // Common subjects for Year 1 (all departments)
        const commonSubjects = [
            { name: 'Engineering Mathematics-I', code: 'MATH101', year: 1, semester: 1, type: 'common', credits: 4 },
            { name: 'Engineering Physics', code: 'PHY101', year: 1, semester: 1, type: 'common', credits: 3 },
            { name: 'Engineering Chemistry', code: 'CHEM101', year: 1, semester: 1, type: 'common', credits: 3 },
            { name: 'English Communication', code: 'ENG101', year: 1, semester: 1, type: 'common', credits: 2 },
            { name: 'Engineering Mathematics-II', code: 'MATH102', year: 1, semester: 2, type: 'common', credits: 4 },
            { name: 'Engineering Graphics', code: 'EG101', year: 1, semester: 2, type: 'common', credits: 3 },
        ];

        for (const sub of commonSubjects) {
            subjects.push({
                ...sub,
                department: null,
                faculty: createdFaculty[Math.floor(Math.random() * createdFaculty.length)]._id
            });
        }

        // Department-specific subjects (Years 2, 3, 4 - 6 subjects per semester)
        for (const dept of createdDepts) {
            const deptFaculty = createdFaculty.filter(f => f.department.toString() === dept._id.toString());
            
            for (let year = 2; year <= 4; year++) {
                for (let sem = 1; sem <= 2; sem++) {
                    const semester = year * 2 + (sem - 2);
                    
                    for (let i = 1; i <= 6; i++) {
                        subjects.push({
                            name: `${dept.code} Subject ${year}${sem}${i}`,
                            code: `${dept.code}${year}${sem}${String(i).padStart(2, '0')}`,
                            department: dept._id,
                            year: year,
                            semester: semester,
                            type: i <= 4 ? 'major' : 'non-major',
                            credits: i <= 4 ? 4 : 3,
                            faculty: deptFaculty[Math.floor(Math.random() * deptFaculty.length)]._id
                        });
                    }
                }
            }
        }

        const createdSubjects = await Subject.insertMany(subjects);
        console.log(`✓ Created ${createdSubjects.length} subjects\n`);

        console.log('='.repeat(60));
        console.log('MOCK DATA GENERATION COMPLETE!');
        console.log('='.repeat(60));
        console.log('\nLogin Credentials:');
        console.log('  COE: coe@mlrit.ac.in / coe123');
        console.log('  Faculty: faculty001@mlrit.ac.in / faculty123');
        console.log('  Student: 714025104001@mlrit.ac.in / student123');
        console.log('\nData Summary:');
        console.log(`  Departments: ${createdDepts.length}`);
        console.log(`  Halls: ${createdHalls.length}`);
        console.log(`  Faculty: ${createdFaculty.length}`);
        console.log(`  Students: ${createdStudents.length}`);
        console.log(`  Subjects: ${createdSubjects.length}`);
        console.log('');

        process.exit(0);
    } catch (error) {
        console.error('Error generating mock data:', error);
        process.exit(1);
    }
}

// Run the generator
generateMockData();
