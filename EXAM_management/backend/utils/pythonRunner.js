const { spawn } = require('child_process');
const path = require('path');
require('dotenv').config();

/**
 * Execute Python script and return results
 * @param {string} scriptPath - Path to Python script
 * @param {Array} args - Command line arguments
 * @param {Object} options - Additional options
 * @returns {Promise} - Promise resolving to script output
 */
function executePythonScript(scriptPath, args = [], options = {}) {
    return new Promise((resolve, reject) => {
        const pythonPath = process.env.PYTHON_PATH || 'python';
        const fullScriptPath = path.resolve(scriptPath);
        
        console.log(`\n${'='.repeat(60)}`);
        console.log(`Executing Python Script: ${path.basename(scriptPath)}`);
        console.log(`${'='.repeat(60)}`);
        console.log(`Python: ${pythonPath}`);
        console.log(`Script: ${fullScriptPath}`);
        console.log(`Args: ${JSON.stringify(args)}`);
        console.log(`${'='.repeat(60)}\n`);

        const pythonProcess = spawn(pythonPath, [fullScriptPath, ...args], {
            cwd: path.dirname(fullScriptPath),
            ...options
        });

        let stdout = '';
        let stderr = '';

        pythonProcess.stdout.on('data', (data) => {
            const output = data.toString();
            stdout += output;
            console.log(output);
        });

        pythonProcess.stderr.on('data', (data) => {
            const error = data.toString();
            stderr += error;
            console.error(error);
        });

        pythonProcess.on('close', (code) => {
            console.log(`\nPython process exited with code ${code}\n`);
            
            if (code === 0) {
                resolve({
                    success: true,
                    stdout,
                    stderr,
                    code
                });
            } else {
                reject({
                    success: false,
                    stdout,
                    stderr,
                    code,
                    message: `Python script failed with exit code ${code}`
                });
            }
        });

        pythonProcess.on('error', (error) => {
            reject({
                success: false,
                error: error.message,
                message: 'Failed to start Python process'
            });
        });
    });
}

/**
 * Run exam scheduling algorithm
 * @param {Object} params - Scheduling parameters
 * @returns {Promise} - Scheduling results with timetable
 */
async function runScheduling(params) {
    const {
        year,
        examType,
        session,
        startDate,
        endDate,
        holidays = [],
        scheduleId
    } = params;

    console.log('Running scheduling algorithm with Python integration...');
    console.log('Scheduling Parameters:', params);
    
    try {
        // Execute Python scheduler to generate timetable
        const scriptPath = path.join(__dirname, '../../modules/scheduler_wrapper.py');
        const paramsJson = JSON.stringify({
            year,
            examType,
            session,
            startDate,
            endDate,
            holidays,
            scheduleId: scheduleId.toString()
        });
        
        const result = await executePythonScript(
            scriptPath,
            ['generate_timetable', paramsJson]
        );
        
        // Parse result
        const output = JSON.parse(result.stdout.trim());
        
        if (!output.success) {
            throw new Error(output.message || 'Scheduling failed');
        }
        
        return {
            success: true,
            message: output.message,
            timetable: output.timetable,
            pdfPath: null // PDF will be generated separately
        };
        
    } catch (error) {
        console.error('Error running scheduling:', error);
        throw error;
    }
}

/**
 * Run seating arrangement algorithm
 * @param {Object} params - Seating parameters
 * @returns {Promise} - Seating results with allocations
 */
async function runSeatingArrangement(params) {
    const {
        year,
        examType,
        session,
        halls,
        scheduleId
    } = params;

    console.log('Running seating arrangement with Python integration...');
    console.log('Seating Arrangement Parameters:', params);
    
    try {
        // Execute Python seating allocator
        const scriptPath = path.join(__dirname, '../../modules/seating_wrapper.py');
        const paramsJson = JSON.stringify({
            year,
            examType,
            session,
            halls: halls.map(h => h.toString()),
            scheduleId: scheduleId.toString()
        });
        
        const result = await executePythonScript(
            scriptPath,
            ['allocate_seats', paramsJson]
        );
        
        // Parse result
        const output = JSON.parse(result.stdout.trim());
        
        if (!output.success) {
            throw new Error(output.message || 'Seating arrangement failed');
        }
        
        return {
            success: true,
            message: output.message,
            allocations: output.allocations,
            totalStudents: output.totalStudents,
            totalHalls: output.totalHalls
        };
        
    } catch (error) {
        console.error('Error running seating arrangement:', error);
        
        // Fallback to mock implementation if Python fails
        console.log('Falling back to mock seating arrangement...');
        const User = require('../models/User');
        
        // Get students for the year
        const students = await User.find({
            role: 'student',
            year: year
        }).select('_id registerNumber name');
        
        // Mock allocation
        const allocations = students.map((student, index) => ({
            studentId: student._id,
            hallId: halls[index % halls.length],
            seatNumber: (index % 30) + 1,
            isLeftSeat: examType !== 'SEM' && (index % 2 === 0)
        }));
        
        return {
            success: true,
            message: 'Seating arrangement completed successfully (fallback)',
            data: {
                totalStudents: students.length,
                hallsUsed: halls.length,
                studentPdfPath: null,
                facultyPdfPath: null
            },
            allocations
        };
    }
}

/**
 * Generate timetable PDF using Python
 * @param {String} scheduleId - Schedule ID
 * @param {String} outputDir - Output directory for PDF
 * @returns {Promise} - PDF generation results
 */
async function generateTimetablePDF(scheduleId, outputDir = 'uploads/timetables') {
    console.log('Generating timetable PDF...');
    
    try {
        const scriptPath = path.join(__dirname, '../../modules/scheduler_wrapper.py');
        const result = await executePythonScript(
            scriptPath,
            ['generate_pdf', scheduleId.toString(), outputDir]
        );
        
        const output = JSON.parse(result.stdout.trim());
        
        if (!output.success) {
            throw new Error(output.message || 'PDF generation failed');
        }
        
        return {
            success: true,
            message: output.message,
            pdfPath: output.pdfPath,
            filename: output.filename
        };
        
    } catch (error) {
        console.error('Error generating timetable PDF:', error);
        throw error;
    }
}

/**
 * Generate seating arrangement PDFs (student and faculty versions)
 * @param {String} scheduleId - Schedule ID
 * @param {String} outputDir - Output directory for PDFs
 * @returns {Promise} - PDF generation results
 */
async function generateSeatingPDFs(scheduleId, outputDir = 'uploads/seating') {
    console.log('Generating seating arrangement PDFs...');
    
    try {
        const scriptPath = path.join(__dirname, '../../modules/seating_wrapper.py');
        
        // Generate student PDF
        const studentResult = await executePythonScript(
            scriptPath,
            ['generate_student_pdf', scheduleId.toString(), outputDir]
        );
        const studentOutput = JSON.parse(studentResult.stdout.trim());
        
        // Generate faculty PDF
        const facultyResult = await executePythonScript(
            scriptPath,
            ['generate_faculty_pdf', scheduleId.toString(), outputDir]
        );
        const facultyOutput = JSON.parse(facultyResult.stdout.trim());
        
        return {
            success: true,
            message: 'Seating PDFs generated successfully',
            studentPdf: {
                path: studentOutput.pdfPath,
                filename: studentOutput.filename
            },
            facultyPdf: {
                path: facultyOutput.pdfPath,
                filename: facultyOutput.filename
            }
        };
        
    } catch (error) {
        console.error('Error generating seating PDFs:', error);
        throw error;
    }
}

/**
 * Generate hall ticket with QR code
 * @param {Object} params - Hall ticket parameters
 * @returns {Promise} - Hall ticket generation results
 */
async function generateHallTicket(params) {
    const {
        studentId,
        registerNumber,
        name,
        examSchedule,
        qrData
    } = params;

    const scriptPath = path.join(__dirname, '../../modules/hall_ticket_generation/server.py');
    
    try {
        const result = await executePythonScript(scriptPath, []);
        
        return {
            success: true,
            message: 'Hall ticket generated successfully',
            data: result.stdout
        };
    } catch (error) {
        console.error('Hall Ticket Generation Error:', error);
        throw new Error(`Hall ticket generation failed: ${error.message}`);
    }
}

/**
 * Generate hall ticket for a single student
 * @param {string} scheduleId - Schedule ID
 * @param {string} registerNumber - Student register number
 * @returns {Promise} - Hall ticket generation result
 */
async function generateSingleHallTicket(scheduleId, registerNumber) {
    console.log('Generating single hall ticket...');
    console.log('Schedule ID:', scheduleId);
    console.log('Register Number:', registerNumber);
    
    try {
        const scriptPath = path.join(__dirname, '../../modules/hall_ticket_wrapper.py');
        
        const result = await executePythonScript(
            scriptPath,
            [scheduleId.toString(), 'generate_single', registerNumber]
        );
        
        // Parse result
        const output = JSON.parse(result.stdout.trim());
        
        if (!output.success) {
            throw new Error(output.error || 'Hall ticket generation failed');
        }
        
        return {
            success: true,
            pdfPath: output.pdfPath,
            registerNumber: output.registerNumber
        };
        
    } catch (error) {
        console.error('Error generating single hall ticket:', error);
        throw error;
    }
}

/**
 * Generate hall tickets for all students in a year
 * @param {string} scheduleId - Schedule ID
 * @param {number} year - Year of study (optional)
 * @returns {Promise} - Bulk hall ticket generation result
 */
async function generateBulkHallTickets(scheduleId, year = null) {
    console.log('Generating bulk hall tickets...');
    console.log('Schedule ID:', scheduleId);
    console.log('Year:', year);
    
    try {
        const scriptPath = path.join(__dirname, '../../modules/hall_ticket_wrapper.py');
        const args = [scheduleId.toString(), 'generate_bulk'];
        
        if (year !== null) {
            args.push(year.toString());
        }
        
        const result = await executePythonScript(scriptPath, args);
        
        // Parse result
        const output = JSON.parse(result.stdout.trim());
        
        if (!output.success) {
            throw new Error(output.error || 'Bulk hall ticket generation failed');
        }
        
        return {
            success: true,
            generated: output.generated,
            errors: output.errors,
            total: output.total,
            successful: output.successful,
            failed: output.failed
        };
        
    } catch (error) {
        console.error('Error generating bulk hall tickets:', error);
        throw error;
    }
}

module.exports = {
    executePythonScript,
    runScheduling,
    runSeatingArrangement,
    generateHallTicket,
    generateTimetablePDF,
    generateSeatingPDFs,
    generateSingleHallTicket,
    generateBulkHallTickets
};
