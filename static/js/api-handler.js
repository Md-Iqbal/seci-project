// API Handler with CSRF token management
class APIHandler {
    constructor() {
        this.baseURL = window.location.origin;
        this.csrfToken = this.getCSRFToken();
    }

    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}/api/${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'X-CSRFToken': this.csrfToken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            credentials: 'same-origin',
        };

        // Handle JSON data
        if (options.body && !(options.body instanceof FormData)) {
            defaultOptions.headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw { status: response.status, data };
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Application methods
    async getApplications(params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const endpoint = queryString ? `applications/?${queryString}` : 'applications/';
        return this.request(endpoint);
    }

    async getApplication(id) {
        return this.request(`applications/${id}/`);
    }

    // Update the createApplication method in api-handler.js
async createApplication(formData) {
    // formData should be a FormData object, not plain object
    const url = `${this.baseURL}/api/applications/`;
    
    const defaultOptions = {
        method: 'POST',
        headers: {
            'X-CSRFToken': this.csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        credentials: 'same-origin',
        body: formData  // FormData object
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        const data = await response.json();
        
        if (!response.ok) {
            throw { status: response.status, data };
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

    async searchByNID(nidNumber) {
        return this.request('applications/search_by_nid/', {
            method: 'POST',
            body: { nid_number: nidNumber }
        });
    }

    async processApplication(id, action, rejectionReason = '') {
        return this.request(`applications/${id}/process/`, {
            method: 'POST',
            body: {
                action: action,
                rejection_reason: rejectionReason
            }
        });
    }

    async getApplicationLogs(id) {
        return this.request(`applications/${id}/logs/`);
    }

    async getDashboardStats() {
        return this.request('dashboard-stats/');
    }
}

// Create global instance
const api = new APIHandler();

// Utility functions
function showLoading(element) {
    const spinner = `
        <div class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading...</p>
        </div>
    `;
    element.innerHTML = spinner;
}

function showError(element, message) {
    element.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="bi bi-exclamation-triangle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function showSuccess(element, message) {
    element.innerHTML = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="bi bi-check-circle"></i> ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function formatDateTime(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

function getStatusBadge(status, statusDisplay) {
    const badges = {
        'PENDING': 'bg-warning',
        'APPROVED': 'bg-success',
        'REJECTED': 'bg-danger'
    };
    return `<span class="badge ${badges[status]}">${statusDisplay}</span>`;
}