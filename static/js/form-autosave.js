/**
 * Form Auto-Save Utility
 * Automatically saves form data to localStorage
 */

class FormAutoSave {
    constructor(formId, storageKey) {
        this.form = document.getElementById(formId);
        this.storageKey = storageKey;
        this.saveInterval = null;
        this.init();
    }

    init() {
        if (!this.form) {
            console.warn(`Form with ID "${this.form}" not found`);
            return;
        }

        // Load saved data on initialization
        this.loadFormData();
        
        // Auto-save on input change
        this.form.querySelectorAll('input, select, textarea').forEach(element => {
            // Skip file inputs and password fields
            if (element.type !== 'file' && element.type !== 'password') {
                element.addEventListener('input', () => this.saveFormData());
            }
        });

        // Auto-save every 30 seconds
        this.saveInterval = setInterval(() => this.saveFormData(), 30000);

        // Clear saved data on successful submit
        this.form.addEventListener('submit', () => {
            setTimeout(() => this.clearFormData(), 1000);
        });

        // Clear interval on page unload
        window.addEventListener('beforeunload', () => {
            if (this.saveInterval) {
                clearInterval(this.saveInterval);
            }
        });
    }

    saveFormData() {
        const formData = new FormData(this.form);
        const data = {};
        let hasData = false;
        
        for (let [key, value] of formData.entries()) {
            // Skip CSRF token, file inputs, and empty values
            if (value && 
                key !== 'csrfmiddlewaretoken' && 
                !key.includes('file') && 
                !key.includes('photograph') &&
                !key.includes('nid_copy') &&
                !key.includes('signature')) {
                data[key] = value;
                hasData = true;
            }
        }
        
        if (hasData) {
            localStorage.setItem(this.storageKey, JSON.stringify(data));
            localStorage.setItem(`${this.storageKey}_timestamp`, Date.now());
            this.showSaveIndicator();
        }
    }

    loadFormData() {
        const savedData = localStorage.getItem(this.storageKey);
        const timestamp = localStorage.getItem(`${this.storageKey}_timestamp`);
        
        if (savedData) {
            // Check if data is not older than 24 hours
            const age = Date.now() - parseInt(timestamp);
            const maxAge = 24 * 60 * 60 * 1000; // 24 hours
            
            if (age > maxAge) {
                this.clearFormData();
                return;
            }
            
            const data = JSON.parse(savedData);
            let hasLoadedData = false;
            
            Object.keys(data).forEach(key => {
                const element = this.form.elements[key];
                if (element && element.type !== 'file') {
                    element.value = data[key];
                    hasLoadedData = true;
                }
            });

            if (hasLoadedData) {
                this.showRestoreNotification();
            }
        }
    }

    clearFormData() {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(`${this.storageKey}_timestamp`);
    }

    showSaveIndicator() {
        let indicator = document.getElementById('autosave-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'autosave-indicator';
            indicator.className = 'bn-text';
            document.body.appendChild(indicator);
        }
        
        indicator.textContent = 'সংরক্ষিত ✓';
        indicator.classList.add('show');
        
        setTimeout(() => {
            indicator.classList.remove('show');
        }, 2000);
    }

    showRestoreNotification() {
        const message = 'সংরক্ষিত তথ্য পাওয়া গেছে। এটি পুনরুদ্ধার করতে চান?';
        
        if (confirm(message)) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show bn-text';
            alert.innerHTML = `
                <i class="bi bi-check-circle"></i>
                সংরক্ষিত তথ্য পুনরুদ্ধার করা হয়েছে
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            const container = document.querySelector('.container');
            if (container) {
                container.insertBefore(alert, container.firstChild);
            }
        } else {
            this.clearFormData();
            location.reload();
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FormAutoSave;
}