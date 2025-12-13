const mongoose = require('mongoose');
const dotenv = require('dotenv');
const path = require('path');

// Load env vars
dotenv.config({ path: path.join(__dirname, '.env') });

// Import models
const User = require('./backend/models/User');
const Department = require('./backend/models/Department');
const Hall = require('./backend/models/Hall');
const Subject = require('./backend/models/Subject');
const Student = require('./backend/models/Student');

// Connect to MongoDB
const connectDB = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI);
        console.log('✓ MongoDB Connected');
    } catch (error) {
        console.error('MongoDB Connection Error:', error);
        process.exit(1);
    }
};

// Clear existing data
const clearData = async () => {
    try {
        await User.deleteMany();
        await Department.deleteMany();
        await Hall.deleteMany();
        await Subject.deleteMany();
        await Student.deleteMany();
        console.log('✓ Existing data cleared');
    } catch (error) {
        console.error('Error clearing data:', error);
    }
};

// Seed Users
const seedUsers = async () => {
    try {
        const users = [
            {
                name: 'Controller of Examinations',
                email: 'coe@mlrit.ac.in',
                password: 'coe123',
                role: 'coe',
                isActive: true
            },
            {
                name: 'Dr. Rajesh Kumar',
                email: 'faculty001@mlrit.ac.in',
                password: 'faculty123',
                role: 'faculty',
                department: 'CSE',
                employeeId: 'FAC001',
                isActive: true
            },
            {
                name: 'Dr. Priya Sharma',
                email: 'faculty002@mlrit.ac.in',
                password: 'faculty123',
                role: 'faculty',
                department: 'ECE',
                employeeId: 'FAC002',
                isActive: true
            },
            {
                name: 'Dr. Anil Verma',
                email: 'faculty003@mlrit.ac.in',
                password: 'faculty123',
                role: 'faculty',
                department: 'MECH',
                employeeId: 'FAC003',
                isActive: true
            },
            {
                name: 'Rahul Reddy',
                email: '714025104001@mlrit.ac.in',
                password: 'student123',
                role: 'student',
                registerNumber: '714025104001',
                department: 'CSE',
                year: 4,
                semester: 8,
                isActive: true
            },
            {
                name: 'Sneha Patel',
                email: '714025104002@mlrit.ac.in',
                password: 'student123',
                role: 'student',
                registerNumber: '714025104002',
                department: 'CSE',
                year: 4,
                semester: 8,
                isActive: true
            }
        ];

        await User.insertMany(users);
        console.log('✓ Users seeded');
        return users;
    } catch (error) {
        console.error('Error seeding users:', error);
    }
};

// Seed Departments
const seedDepartments = async () => {
    try {
        const departments = [
            {
                name: 'Computer Science and Engineering',
                code: 'CSE',
                hod: 'Dr. Rajesh Kumar',
                totalStudents: 120,
                isActive: true
            },
            {
                name: 'Electronics and Communication Engineering',
                code: 'ECE',
                hod: 'Dr. Priya Sharma',
                totalStudents: 90,
                isActive: true
            },
            {
                name: 'Mechanical Engineering',
                code: 'MECH',
                hod: 'Dr. Anil Verma',
                totalStudents: 60,
                isActive: true
            },
            {
                name: 'Civil Engineering',
                code: 'CIVIL',
                hod: 'Dr. Suresh Babu',
                totalStudents: 50,
                isActive: true
            }
        ];

        const createdDepts = await Department.insertMany(departments);
        console.log('✓ Departments seeded');
        return createdDepts;
    } catch (error) {
        console.error('Error seeding departments:', error);
    }
};

// Seed Halls
const seedHalls = async () => {
    try {
        const halls = [
            {
                hallNumber: 'A-101',
                building: 'Block A',
                capacity: 30,
                examCapacity: 15,
                columns: 5,
                floor: 1,
                facilities: ['Projector', 'AC', 'CCTV'],
                isActive: true
            },
            {
                hallNumber: 'A-102',
                building: 'Block A',
                capacity: 32,
                examCapacity: 16,
                columns: 4,
                floor: 1,
                facilities: ['Projector', 'AC', 'CCTV'],
                isActive: true
            },
            {
                hallNumber: 'B-201',
                building: 'Block B',
                capacity: 35,
                examCapacity: 18,
                columns: 5,
                floor: 2,
                facilities: ['Projector', 'AC', 'CCTV'],
                isActive: true
            },
            {
                hallNumber: 'B-202',
                building: 'Block B',
                capacity: 33,
                examCapacity: 17,
                columns: 6,
                floor: 2,
                facilities: ['Projector', 'AC', 'CCTV'],
                isActive: true
            },
            {
                hallNumber: 'C-301',
                building: 'Block C',
                capacity: 34,
                examCapacity: 17,
                columns: 6,
                floor: 3,
                facilities: ['Projector', 'AC', 'CCTV', 'Smart Board'],
                isActive: true
            },
            {
                hallNumber: 'C-302',
                building: 'Block C',
                capacity: 35,
                examCapacity: 18,
                columns: 5,
                floor: 3,
                facilities: ['Projector', 'AC', 'CCTV', 'Smart Board'],
                isActive: true
            }
        ];

        const createdHalls = await Hall.insertMany(halls);
        console.log('✓ Halls seeded');
        return createdHalls;
    } catch (error) {
        console.error('Error seeding halls:', error);
    }
};

// Seed Subjects
const seedSubjects = async (departments) => {
    try {
        const cse = departments.find(d => d.code === 'CSE');
        const ece = departments.find(d => d.code === 'ECE');
        const mech = departments.find(d => d.code === 'MECH');

        const subjects = [
            // Year 1 Common Subjects
            {
                code: 'MA101',
                name: 'Engineering Mathematics-I',
                department: cse._id,
                year: 1,
                semester: 1,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'PH101',
                name: 'Engineering Physics',
                department: cse._id,
                year: 1,
                semester: 1,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'CS101',
                name: 'Programming for Problem Solving',
                department: cse._id,
                year: 1,
                semester: 1,
                credits: 3,
                type: 'Theory',
                isActive: true
            },
            // Year 2 CSE
            {
                code: 'CS201',
                name: 'Data Structures',
                department: cse._id,
                year: 2,
                semester: 3,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'CS202',
                name: 'Database Management Systems',
                department: cse._id,
                year: 2,
                semester: 3,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            // Year 3 CSE
            {
                code: 'CS301',
                name: 'Operating Systems',
                department: cse._id,
                year: 3,
                semester: 5,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'CS302',
                name: 'Computer Networks',
                department: cse._id,
                year: 3,
                semester: 5,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            // Year 4 CSE
            {
                code: 'CS401',
                name: 'Machine Learning',
                department: cse._id,
                year: 4,
                semester: 7,
                credits: 4,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'CS402',
                name: 'Cloud Computing',
                department: cse._id,
                year: 4,
                semester: 7,
                credits: 3,
                type: 'Theory',
                isActive: true
            },
            {
                code: 'CS403',
                name: 'Big Data Analytics',
                department: cse._id,
                year: 4,
                semester: 8,
                credits: 3,
                type: 'Theory',
                isActive: true
            }
        ];

        const createdSubjects = await Subject.insertMany(subjects);
        console.log('✓ Subjects seeded');
        return createdSubjects;
    } catch (error) {
        console.error('Error seeding subjects:', error);
    }
};

// Seed Students
const seedStudents = async (departments) => {
    try {
        const cse = departments.find(d => d.code === 'CSE');
        const ece = departments.find(d => d.code === 'ECE');
        const mech = departments.find(d => d.code === 'MECH');
        const civil = departments.find(d => d.code === 'CIVIL');

        // Realistic Indian names
        const maleNames = [
            'Rahul Reddy', 'Karthik Kumar', 'Aditya Sharma', 'Sai Krishna', 'Vijay Varma',
            'Rohan Patel', 'Arjun Singh', 'Akash Gupta', 'Nikhil Rao', 'Pranav Mehta',
            'Harish Nair', 'Suresh Babu', 'Manoj Kumar', 'Rakesh Reddy', 'Naveen Chandra',
            'Deepak Verma', 'Anil Kumar', 'Ravi Teja', 'Sandeep Reddy', 'Mahesh Babu',
            'Venkat Rao', 'Lokesh Kumar', 'Pavan Kalyan', 'Chetan Singh', 'Varun Tej',
            'Siddharth Reddy', 'Anand Kumar', 'Rajesh Nair', 'Girish Patel', 'Ashwin Rao'
        ];

        const femaleNames = [
            'Sneha Patel', 'Priya Sharma', 'Divya Reddy', 'Anjali Singh', 'Kavya Kumar',
            'Pooja Nair', 'Swathi Rao', 'Meera Gupta', 'Nidhi Verma', 'Shruti Patel',
            'Ananya Reddy', 'Lavanya Kumar', 'Sravani Nair', 'Keerthi Rao', 'Manasa Sharma',
            'Pallavi Singh', 'Sahithi Reddy', 'Varsha Kumar', 'Tejasvi Patel', 'Anusha Rao',
            'Swapna Reddy', 'Deepika Kumar', 'Harini Nair', 'Bhavana Sharma', 'Madhuri Patel',
            'Archana Reddy', 'Swetha Kumar', 'Ramya Rao', 'Lakshmi Nair', 'Sowmya Sharma'
        ];

        const students = [];
        let nameIndex = 0;
        
        // Helper function to get next name
        const getNextName = (gender) => {
            const names = gender === 'Male' ? maleNames : femaleNames;
            const name = names[nameIndex % names.length];
            nameIndex++;
            return name;
        };

        // Year 1 students - CSE (30 students)
        for (let i = 1; i <= 30; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `724025104${String(i).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `724025104${String(i).padStart(3, '0')}@mlrit.ac.in`,
                department: cse._id,
                year: 1,
                semester: 1,
                batch: '2024-2028',
                dateOfBirth: new Date(2006, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(40000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 1 students - ECE (25 students)
        for (let i = 31; i <= 55; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `724025105${String(i - 30).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `724025105${String(i - 30).padStart(3, '0')}@mlrit.ac.in`,
                department: ece._id,
                year: 1,
                semester: 1,
                batch: '2024-2028',
                dateOfBirth: new Date(2006, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(40000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 2 students - CSE (30 students)
        for (let i = 1; i <= 30; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `723025104${String(i).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `723025104${String(i).padStart(3, '0')}@mlrit.ac.in`,
                department: cse._id,
                year: 2,
                semester: 1,
                batch: '2023-2027',
                dateOfBirth: new Date(2005, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(50000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 2 students - ECE (25 students)
        for (let i = 31; i <= 55; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `723025105${String(i - 30).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `723025105${String(i - 30).padStart(3, '0')}@mlrit.ac.in`,
                department: ece._id,
                year: 2,
                semester: 1,
                batch: '2023-2027',
                dateOfBirth: new Date(2005, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(50000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 3 students - CSE (30 students)
        for (let i = 1; i <= 30; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `722025104${String(i).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `722025104${String(i).padStart(3, '0')}@mlrit.ac.in`,
                department: cse._id,
                year: 3,
                semester: 1,
                batch: '2022-2026',
                dateOfBirth: new Date(2004, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(60000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 3 students - MECH (20 students)
        for (let i = 31; i <= 50; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `722025106${String(i - 30).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `722025106${String(i - 30).padStart(3, '0')}@mlrit.ac.in`,
                department: mech._id,
                year: 3,
                semester: 1,
                batch: '2022-2026',
                dateOfBirth: new Date(2004, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(60000 + i).padStart(5, '0')}`,
                regulation: 'R22',
                isActive: true
            });
        }

        // Year 4 students - CSE (30 students) - including login user
        for (let i = 1; i <= 30; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `714025104${String(i).padStart(3, '0')}`,
                name: i === 1 ? 'Rahul Reddy' : getNextName(gender),
                email: `714025104${String(i).padStart(3, '0')}@mlrit.ac.in`,
                department: cse._id,
                year: 4,
                semester: 1,
                batch: '2021-2025',
                dateOfBirth: new Date(2003, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(70000 + i).padStart(5, '0')}`,
                regulation: 'R18',
                isActive: true
            });
        }

        // Year 4 students - ECE (25 students)
        for (let i = 31; i <= 55; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `714025105${String(i - 30).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `714025105${String(i - 30).padStart(3, '0')}@mlrit.ac.in`,
                department: ece._id,
                year: 4,
                semester: 1,
                batch: '2021-2025',
                dateOfBirth: new Date(2003, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(70000 + i).padStart(5, '0')}`,
                regulation: 'R18',
                isActive: true
            });
        }

        // Year 4 students - CIVIL (20 students)
        for (let i = 56; i <= 75; i++) {
            const gender = i % 2 === 0 ? 'Male' : 'Female';
            students.push({
                registerNumber: `714025107${String(i - 55).padStart(3, '0')}`,
                name: getNextName(gender),
                email: `714025107${String(i - 55).padStart(3, '0')}@mlrit.ac.in`,
                department: civil._id,
                year: 4,
                semester: 1,
                batch: '2021-2025',
                dateOfBirth: new Date(2003, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1),
                gender: gender,
                phoneNumber: `98765${String(70000 + i).padStart(5, '0')}`,
                regulation: 'R18',
                isActive: true
            });
        }

        const createdStudents = await Student.insertMany(students);
        console.log(`✓ ${createdStudents.length} Students seeded across all departments`);
        console.log(`  - Year 1: ${students.filter(s => s.year === 1).length} students`);
        console.log(`  - Year 2: ${students.filter(s => s.year === 2).length} students`);
        console.log(`  - Year 3: ${students.filter(s => s.year === 3).length} students`);
        console.log(`  - Year 4: ${students.filter(s => s.year === 4).length} students`);
        return createdStudents;
    } catch (error) {
        console.error('Error seeding students:', error);
    }
};

// Main seed function
const seedDatabase = async () => {
    try {
        await connectDB();
        
        console.log('\n🌱 Starting database seeding...\n');
        
        await clearData();
        
        await seedUsers();
        const departments = await seedDepartments();
        await seedHalls();
        await seedSubjects(departments);
        await seedStudents(departments);
        
        console.log('\n✅ Database seeding completed successfully!\n');
        console.log('You can now login with:');
        console.log('  COE: coe@mlrit.ac.in / coe123');
        console.log('  Faculty: faculty001@mlrit.ac.in / faculty123');
        console.log('  Student: 714025104001@mlrit.ac.in / student123\n');
        
        process.exit(0);
    } catch (error) {
        console.error('Error seeding database:', error);
        process.exit(1);
    }
};

// Run seeder
seedDatabase();
