const QRCode = require('qrcode');
const crypto = require('crypto');

/**
 * Generate QR code data string with encryption
 * @param {Object} data - Data to encode in QR
 * @returns {Promise<string>} - QR code data URL
 */
async function generateQRCode(data) {
    try {
        // Create signature for verification
        const signature = createSignature(data);
        
        // Combine data with signature
        const qrData = {
            ...data,
            signature
        };

        // Convert to JSON string
        const dataString = JSON.stringify(qrData);

        // Generate QR code as data URL
        const qrDataURL = await QRCode.toDataURL(dataString, {
            errorCorrectionLevel: 'H',
            type: 'image/png',
            quality: 0.95,
            margin: 1,
            width: 300
        });

        return qrDataURL;
    } catch (error) {
        console.error('QR Code Generation Error:', error);
        throw new Error('Failed to generate QR code');
    }
}

/**
 * Create digital signature for QR data
 * @param {Object} data - Data to sign
 * @returns {string} - Signature hash
 */
function createSignature(data) {
    const secret = process.env.JWT_SECRET || 'default_secret';
    const dataString = JSON.stringify(data);
    
    return crypto
        .createHmac('sha256', secret)
        .update(dataString)
        .digest('hex');
}

/**
 * Verify QR code signature
 * @param {Object} qrData - QR code data with signature
 * @returns {boolean} - Verification result
 */
function verifySignature(qrData) {
    try {
        const { signature, ...data } = qrData;
        const expectedSignature = createSignature(data);
        
        return signature === expectedSignature;
    } catch (error) {
        console.error('Signature Verification Error:', error);
        return false;
    }
}

/**
 * Parse QR code data
 * @param {string} qrString - QR code string
 * @returns {Object} - Parsed data
 */
function parseQRCode(qrString) {
    try {
        const data = JSON.parse(qrString);
        return data;
    } catch (error) {
        console.error('QR Parse Error:', error);
        throw new Error('Invalid QR code format');
    }
}

/**
 * Check if QR scanning is allowed based on exam time
 * @param {Date} examStartTime - Exam start time
 * @param {number} windowMinutes - Time window in minutes (default 30)
 * @returns {boolean} - Whether scanning is allowed
 */
function isQRScanningAllowed(examStartTime, windowMinutes = 30) {
    const now = new Date();
    const examTime = new Date(examStartTime);
    const diffMinutes = (examTime - now) / (1000 * 60);
    
    // Allow scanning from 30 minutes before to 30 minutes after exam start
    return (diffMinutes >= -windowMinutes && diffMinutes <= windowMinutes);
}

/**
 * Get remaining time for QR scanning window
 * @param {Date} examStartTime - Exam start time
 * @param {number} windowMinutes - Time window in minutes
 * @returns {Object} - Time information
 */
function getScanningWindow(examStartTime, windowMinutes = 30) {
    const now = new Date();
    const examTime = new Date(examStartTime);
    const windowStart = new Date(examTime.getTime() - windowMinutes * 60 * 1000);
    const windowEnd = new Date(examTime.getTime() + windowMinutes * 60 * 1000);
    
    const isAllowed = isQRScanningAllowed(examStartTime, windowMinutes);
    
    let message = '';
    if (now < windowStart) {
        const minutesUntilStart = Math.floor((windowStart - now) / (1000 * 60));
        message = `Scanning opens in ${minutesUntilStart} minutes`;
    } else if (now > windowEnd) {
        message = 'Scanning window closed';
    } else {
        const minutesRemaining = Math.floor((windowEnd - now) / (1000 * 60));
        message = `${minutesRemaining} minutes remaining`;
    }
    
    return {
        isAllowed,
        windowStart,
        windowEnd,
        currentTime: now,
        message
    };
}

module.exports = {
    generateQRCode,
    createSignature,
    verifySignature,
    parseQRCode,
    isQRScanningAllowed,
    getScanningWindow
};
