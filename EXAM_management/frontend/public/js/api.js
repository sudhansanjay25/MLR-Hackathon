// API utility functions

const API_BASE_URL = window.location.origin;

// Generic API call function
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies
    };

    const config = { ...defaultOptions, ...options };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.message || 'API call failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Logout function
async function logout() {
    try {
        await fetch('/api/auth/logout');
        window.location.href = '/';
    } catch (error) {
        console.error('Logout error:', error);
        alert('Failed to logout');
    }
}

// Export if using modules, otherwise functions are global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { apiCall, logout };
}
