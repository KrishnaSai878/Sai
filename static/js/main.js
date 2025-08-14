// Main JavaScript functionality for NGO Platform

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Initialize modals
    initializeModals();
    
    // Setup file upload enhancements
    setupFileUploads();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup dashboard counters
    setupCounterAnimations();
    
    // Setup search functionality
    setupSearchFilters();
    
    // Setup confirmation dialogs
    setupConfirmationDialogs();
    
    // Auto-refresh notifications
    setupNotificationRefresh();
});

// Initialize modal functionality
function initializeModals() {
    const modalTriggers = document.querySelectorAll('[data-modal-target]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function(e) {
            e.preventDefault();
            const targetModal = document.querySelector(this.dataset.modalTarget);
            if (targetModal && typeof bootstrap !== 'undefined') {
                const modal = new bootstrap.Modal(targetModal);
                modal.show();
            }
        });
    });
}

// Enhanced file upload functionality
function setupFileUploads() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        const wrapper = input.closest('.mb-3') || input.parentElement;
        
        // Create drag and drop area
        if (!wrapper.querySelector('.file-upload-area')) {
            createDragDropArea(input, wrapper);
        }
        
        // File validation
        input.addEventListener('change', function(e) {
            validateFile(e.target);
        });
    });
}

// Create drag and drop upload area
function createDragDropArea(input, wrapper) {
    const dragArea = document.createElement('div');
    dragArea.className = 'file-upload-area mt-2';
    dragArea.innerHTML = `
        <i data-feather="upload-cloud" style="width: 48px; height: 48px;" class="text-muted mb-2"></i>
        <p class="mb-2">Drag and drop your file here or click to browse</p>
        <small class="text-muted">Supported formats: JPG, PNG, JPEG (max 16MB)</small>
    `;
    
    // Insert after the file input
    input.parentNode.insertBefore(dragArea, input.nextSibling);
    
    // Make it clickable
    dragArea.addEventListener('click', () => input.click());
    
    // Drag and drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dragArea.addEventListener(eventName, preventDefaults);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dragArea.addEventListener(eventName, () => dragArea.classList.add('dragover'));
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dragArea.addEventListener(eventName, () => dragArea.classList.remove('dragover'));
    });
    
    dragArea.addEventListener('drop', function(e) {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            validateFile(input);
        }
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// File validation
function validateFile(input) {
    const file = input.files[0];
    const wrapper = input.closest('.mb-3') || input.parentElement;
    
    // Remove previous validation messages
    const existingFeedback = wrapper.querySelector('.file-feedback');
    if (existingFeedback) {
        existingFeedback.remove();
    }
    
    if (!file) return;
    
    const feedback = document.createElement('div');
    feedback.className = 'file-feedback mt-2';
    
    // Check file size (16MB limit)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        feedback.innerHTML = `<small class="text-danger">File too large. Maximum size is 16MB.</small>`;
        input.value = '';
    }
    // Check file type
    else if (!file.type.match(/^image\/(jpeg|jpg|png)$/)) {
        feedback.innerHTML = `<small class="text-danger">Invalid file type. Please select a JPG, PNG, or JPEG image.</small>`;
        input.value = '';
    }
    // Valid file
    else {
        const sizeInMB = (file.size / 1024 / 1024).toFixed(2);
        feedback.innerHTML = `<small class="text-success">
            <i data-feather="check-circle" style="width: 14px; height: 14px;"></i>
            File selected: ${file.name} (${sizeInMB} MB)
        </small>`;
    }
    
    wrapper.appendChild(feedback);
    
    // Refresh feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

// Form validation enhancements
function setupFormValidations() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Real-time validation for specific fields
        const emailInputs = form.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', validateEmail);
        });
        
        const passwordInputs = form.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            if (input.name === 'password') {
                input.addEventListener('input', validatePassword);
            }
        });
        
        // Form submission loading state
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    ${submitBtn.textContent}
                `;
                
                // Re-enable after 3 seconds to prevent permanent lockout
                setTimeout(() => {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.textContent.replace(/^\s*/, '');
                }, 3000);
            }
        });
    });
}

// Email validation
function validateEmail(e) {
    const input = e.target;
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    const feedback = getOrCreateFeedback(input);
    
    if (email && !emailRegex.test(email)) {
        feedback.innerHTML = '<small class="text-danger">Please enter a valid email address.</small>';
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
    } else if (email) {
        feedback.innerHTML = '<small class="text-success">Valid email address.</small>';
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    } else {
        feedback.innerHTML = '';
        input.classList.remove('is-valid', 'is-invalid');
    }
}

// Password validation
function validatePassword(e) {
    const input = e.target;
    const password = input.value;
    const feedback = getOrCreateFeedback(input);
    
    const requirements = [
        { test: password.length >= 6, text: 'At least 6 characters' },
        { test: /[A-Z]/.test(password), text: 'One uppercase letter' },
        { test: /[a-z]/.test(password), text: 'One lowercase letter' },
        { test: /\d/.test(password), text: 'One number' }
    ];
    
    if (password) {
        const passed = requirements.filter(req => req.test).length;
        const strength = passed <= 1 ? 'weak' : passed <= 2 ? 'medium' : passed <= 3 ? 'good' : 'strong';
        const strengthColors = { weak: 'danger', medium: 'warning', good: 'info', strong: 'success' };
        
        feedback.innerHTML = `
            <small class="text-${strengthColors[strength]}">
                Password strength: ${strength}
                (${passed}/4 requirements met)
            </small>
        `;
        
        input.classList.toggle('is-valid', strength === 'strong');
        input.classList.toggle('is-invalid', strength === 'weak');
    } else {
        feedback.innerHTML = '';
        input.classList.remove('is-valid', 'is-invalid');
    }
}

// Get or create feedback element
function getOrCreateFeedback(input) {
    let feedback = input.parentNode.querySelector('.validation-feedback');
    if (!feedback) {
        feedback = document.createElement('div');
        feedback.className = 'validation-feedback';
        input.parentNode.appendChild(feedback);
    }
    return feedback;
}

// Counter animations for dashboard stats
function setupCounterAnimations() {
    const counters = document.querySelectorAll('[data-counter]');
    
    counters.forEach(counter => {
        const target = parseInt(counter.dataset.counter || counter.textContent);
        const duration = parseInt(counter.dataset.duration) || 2000;
        
        animateCounter(counter, 0, target, duration);
    });
}

function animateCounter(element, start, end, duration) {
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * easeOutQuart(progress));
        element.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = end;
        }
    }
    
    requestAnimationFrame(updateCounter);
}

function easeOutQuart(t) {
    return 1 - Math.pow(1 - t, 4);
}

// Search and filter functionality
function setupSearchFilters() {
    const searchInputs = document.querySelectorAll('[data-search-target]');
    
    searchInputs.forEach(input => {
        const targetSelector = input.dataset.searchTarget;
        const targets = document.querySelectorAll(targetSelector);
        
        input.addEventListener('input', function() {
            const query = this.value.toLowerCase();
            
            targets.forEach(target => {
                const text = target.textContent.toLowerCase();
                const matches = text.includes(query);
                
                target.style.display = matches ? '' : 'none';
            });
        });
    });
}

// Confirmation dialogs
function setupConfirmationDialogs() {
    const confirmLinks = document.querySelectorAll('[data-confirm]');
    
    confirmLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const message = this.dataset.confirm;
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

// Auto-refresh notifications for admins
function setupNotificationRefresh() {
    const notificationElements = document.querySelectorAll('[data-auto-refresh]');
    
    notificationElements.forEach(element => {
        const interval = parseInt(element.dataset.autoRefresh) || 30000; // Default 30 seconds
        
        setInterval(() => {
            // In a real implementation, this would make an AJAX call to get updated counts
            // For now, we'll just add a subtle indicator that data is being refreshed
            element.style.opacity = '0.7';
            setTimeout(() => {
                element.style.opacity = '1';
            }, 200);
        }, interval);
    });
}

// Utility functions

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Show toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 5000);
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Copied to clipboard!', 'success');
    }
}

// Export function for data tables
function exportTableToCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => `"${cell.textContent.replace(/"/g, '""')}"`).join(',');
    }).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
}

// Global error handler
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // In production, you might want to send this to a logging service
});

// Make some functions globally available
window.NGOPlatform = {
    formatCurrency,
    formatDate,
    showToast,
    copyToClipboard,
    exportTableToCSV
};
