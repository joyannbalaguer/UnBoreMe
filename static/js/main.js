/**
 * Main JavaScript for Flask Gaming Platform
 * Shared functionality across all pages
 */

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message, .alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Close button for flash messages
    const closeButtons = document.querySelectorAll('.flash-close, .alert-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const message = this.parentElement;
            message.style.transition = 'opacity 0.3s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        });
    });
});

// Form validation helper
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    let isValid = true;
    
    inputs.forEach(function(input) {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Email validation
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(String(email).toLowerCase());
}

// Password strength checker
function checkPasswordStrength(password) {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^a-zA-Z0-9]/.test(password)) strength++;
    
    if (strength < 3) return 'weak';
    if (strength < 5) return 'medium';
    return 'strong';
}

// Show password strength indicator
function updatePasswordStrength(inputId, indicatorId) {
    const input = document.getElementById(inputId);
    const indicator = document.getElementById(indicatorId);
    
    if (!input || !indicator) return;
    
    input.addEventListener('input', function() {
        const strength = checkPasswordStrength(this.value);
        indicator.className = 'password-strength-indicator ' + strength;
        indicator.textContent = 'Password strength: ' + strength.toUpperCase();
    });
}

// Blog Post Delete Confirmation with SweetAlert2 (matches admin style)
function confirmDeletePost(postId) {
    Swal.fire({
        title: 'Delete this post?',
        text: 'This action is permanent and cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete',
        cancelButtonText: 'Cancel',
        background: '#12121a',
        color: '#ffffff',
        customClass: {
            popup: 'swal2-popup-dark',
            title: 'swal2-title-dark',
            content: 'swal2-content-dark',
            confirmButton: 'swal2-confirm-danger',
            cancelButton: 'swal2-cancel-dark'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById('delete-form-' + postId).submit();
        }
    });
}

// Blog Post Edit Confirmation with SweetAlert2 (matches admin style)
function confirmEditPost(editUrl) {
    Swal.fire({
        title: 'Are you sure?',
        text: 'Do you want to edit this post?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, edit',
        cancelButtonText: 'Cancel',
        background: '#12121a',
        color: '#ffffff',
        customClass: {
            popup: 'swal2-popup-dark',
            title: 'swal2-title-dark',
            content: 'swal2-content-dark',
            confirmButton: 'swal2-confirm-dark',
            cancelButton: 'swal2-cancel-dark'
        }
    }).then((result) => {
        if (result.isConfirmed) {
            window.location.href = editUrl;
        }
    });
}

// Loading spinner
function showLoading(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Loading...';
    }
}

function hideLoading(buttonId, originalText) {
    const button = document.getElementById(buttonId);
    if (button) {
        button.disabled = false;
        button.innerHTML = originalText;
    }
}

// Countdown timer (for OTP expiry)
function startCountdown(elementId, seconds) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    let remaining = seconds;
    
    const interval = setInterval(function() {
        const minutes = Math.floor(remaining / 60);
        const secs = remaining % 60;
        element.textContent = minutes + ':' + (secs < 10 ? '0' : '') + secs;
        
        remaining--;
        
        if (remaining < 0) {
            clearInterval(interval);
            element.textContent = 'Expired';
            element.classList.add('expired');
        }
    }, 1000);
}

// Resend OTP cooldown timer
function startResendCooldown(buttonId, seconds) {
    const button = document.getElementById(buttonId);
    if (!button) return;
    
    let remaining = seconds;
    button.disabled = true;
    
    const interval = setInterval(function() {
        button.textContent = 'Resend OTP (' + remaining + 's)';
        remaining--;
        
        if (remaining < 0) {
            clearInterval(interval);
            button.disabled = false;
            button.textContent = 'Resend OTP';
        }
    }, 1000);
}

// Character counter for textareas
function addCharacterCounter(textareaId, counterId, maxLength) {
    const textarea = document.getElementById(textareaId);
    const counter = document.getElementById(counterId);
    
    if (!textarea || !counter) return;
    
    textarea.addEventListener('input', function() {
        const length = this.value.length;
        counter.textContent = length + ' / ' + maxLength;
        
        if (length > maxLength) {
            counter.classList.add('exceeded');
        } else {
            counter.classList.remove('exceeded');
        }
    });
}

// Toggle password visibility
function togglePasswordVisibility(inputId, toggleBtnId) {
    const input = document.getElementById(inputId);
    const button = document.getElementById(toggleBtnId);
    
    if (!input || !button) return;
    
    button.addEventListener('click', function() {
        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = '🙈';
            button.title = 'Hide password';
        } else {
            input.type = 'password';
            button.textContent = '👁️';
            button.title = 'Show password';
        }
    });
}

// Smooth scroll to element
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Format date/time
function formatDateTime(dateString) {
    const date = new Date(dateString);
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

// Debounce function (useful for search inputs)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Copy to clipboard
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showNotification('Copied to clipboard!', 'success');
        }).catch(function(err) {
            console.error('Failed to copy: ', err);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Copied to clipboard!', 'success');
    }
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = 'notification notification-' + (type || 'info');
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(function() {
        notification.classList.remove('show');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

// AJAX helper
function ajaxRequest(url, method, data, successCallback, errorCallback) {
    fetch(url, {
        method: method || 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: data ? JSON.stringify(data) : null
    })
    .then(response => response.json())
    .then(data => {
        if (successCallback) successCallback(data);
    })
    .catch(error => {
        if (errorCallback) errorCallback(error);
        else console.error('AJAX Error:', error);
    });
}

// Hamburger Mobile Menu Toggle
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');
    
    if (hamburger && navLinks) {
        // Toggle menu on hamburger click
        hamburger.addEventListener('click', function(e) {
            e.stopPropagation();
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active');
        });
        
        // Close menu when clicking on a nav link
        const links = navLinks.querySelectorAll('.nav-link');
        links.forEach(function(link) {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navLinks.contains(e.target) && !hamburger.contains(e.target)) {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active');
            }
        });
    }
    
    // Legacy mobile menu toggle (if exists)
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
            this.classList.toggle('active');
        });
    }
});

// Form auto-save (to localStorage)
function enableFormAutoSave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    // Load saved data
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(function(key) {
            const input = form.querySelector('[name="' + key + '"]');
            if (input) input.value = data[key];
        });
    }
    
    // Save on input
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(function(input) {
        input.addEventListener('input', debounce(function() {
            const formData = {};
            const formInputs = form.querySelectorAll('input, textarea, select');
            formInputs.forEach(function(inp) {
                if (inp.name) formData[inp.name] = inp.value;
            });
            localStorage.setItem(storageKey, JSON.stringify(formData));
        }, 500));
    });
    
    // Clear on submit
    form.addEventListener('submit', function() {
        localStorage.removeItem(storageKey);
    });
}

// Image preview for file uploads
function previewImage(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    if (!input || !preview) return;
    
    input.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

// Table search/filter
function filterTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', debounce(function() {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(function(row) {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    }, 300));
}

// Export utilities
window.FlaskGamingPlatform = {
    validateForm,
    validateEmail,
    checkPasswordStrength,
    updatePasswordStrength,
    confirmAction,
    confirmDelete,
    showLoading,
    hideLoading,
    startCountdown,
    startResendCooldown,
    addCharacterCounter,
    togglePasswordVisibility,
    smoothScrollTo,
    formatDateTime,
    debounce,
    copyToClipboard,
    showNotification,
    ajaxRequest,
    enableFormAutoSave,
    previewImage,
    filterTable
};
