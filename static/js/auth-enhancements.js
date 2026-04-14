// Authentication form enhancements
document.addEventListener('DOMContentLoaded', function() {
    
    // Form validation and UX improvements
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required]');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        // Real-time validation
        inputs.forEach(input => {
            input.addEventListener('blur', validateField);
            input.addEventListener('input', clearErrors);
        });
        
        // Form submission with loading state
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                return;
            }
            
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Please wait...';
                submitBtn.disabled = true;
                
                // Re-enable after 5 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 5000);
            }
        });
    });
    
    // Password strength indicator for signup
    const passwordInput = document.getElementById('id_password1');
    if (passwordInput) {
        const strengthIndicator = createPasswordStrengthIndicator();
        passwordInput.parentNode.appendChild(strengthIndicator);
        
        passwordInput.addEventListener('input', function() {
            updatePasswordStrength(this.value, strengthIndicator);
        });
    }
    
    // Password confirmation validation
    const confirmPasswordInput = document.getElementById('id_password2');
    if (confirmPasswordInput && passwordInput) {
        confirmPasswordInput.addEventListener('input', function() {
            validatePasswordConfirmation(passwordInput.value, this.value, this);
        });
    }
    
    // Social login button animations
    const socialBtns = document.querySelectorAll('.btn-social, .social-btn');
    socialBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            // Add loading animation
            const originalContent = this.innerHTML;
            this.innerHTML = '<i class="bi bi-hourglass-split"></i> Connecting...';
            this.style.pointerEvents = 'none';
            
            // Restore after 3 seconds if still on page
            setTimeout(() => {
                this.innerHTML = originalContent;
                this.style.pointerEvents = 'auto';
            }, 3000);
        });
    });
    
    // Floating label animation
    const floatingInputs = document.querySelectorAll('.form-input');
    floatingInputs.forEach(input => {
        // Check if input has value on page load
        if (input.value.trim() !== '') {
            input.classList.add('has-value');
        }
        
        input.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('focused');
            if (this.value.trim() !== '') {
                this.classList.add('has-value');
            } else {
                this.classList.remove('has-value');
            }
        });
    });
});

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    
    // Remove existing error messages
    clearFieldError(field);
    
    // Email validation
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Password validation
    if (field.type === 'password' && field.id === 'id_password1' && value) {
        if (value.length < 8) {
            showFieldError(field, 'Password must be at least 8 characters long');
            return false;
        }
    }
    
    // Required field validation
    if (field.hasAttribute('required') && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    return true;
}

function clearErrors(e) {
    clearFieldError(e.target);
}

function validateForm(form) {
    const inputs = form.querySelectorAll('input[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!validateField({ target: input })) {
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error text-danger small mt-1';
    errorDiv.innerHTML = `<i class="bi bi-exclamation-circle me-1"></i>${message}`;
    
    field.parentNode.appendChild(errorDiv);
    field.classList.add('is-invalid');
}

function clearFieldError(field) {
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    field.classList.remove('is-invalid');
}

function createPasswordStrengthIndicator() {
    const container = document.createElement('div');
    container.className = 'password-strength mt-2';
    container.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill"></div>
        </div>
        <div class="strength-text small text-muted mt-1">Password strength</div>
    `;
    
    // Add CSS for password strength indicator
    const style = document.createElement('style');
    style.textContent = `
        .strength-bar {
            height: 4px;
            background: #e1e5e9;
            border-radius: 2px;
            overflow: hidden;
        }
        .strength-fill {
            height: 100%;
            width: 0%;
            transition: all 0.3s ease;
            border-radius: 2px;
        }
        .strength-weak .strength-fill { width: 25%; background: #dc3545; }
        .strength-fair .strength-fill { width: 50%; background: #fd7e14; }
        .strength-good .strength-fill { width: 75%; background: #ffc107; }
        .strength-strong .strength-fill { width: 100%; background: #28a745; }
    `;
    document.head.appendChild(style);
    
    return container;
}

function updatePasswordStrength(password, indicator) {
    const strengthText = indicator.querySelector('.strength-text');
    const container = indicator;
    
    // Remove existing strength classes
    container.classList.remove('strength-weak', 'strength-fair', 'strength-good', 'strength-strong');
    
    if (password.length === 0) {
        strengthText.textContent = 'Password strength';
        return;
    }
    
    let score = 0;
    
    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Character variety checks
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    
    // Determine strength
    if (score <= 2) {
        container.classList.add('strength-weak');
        strengthText.textContent = 'Weak password';
    } else if (score <= 3) {
        container.classList.add('strength-fair');
        strengthText.textContent = 'Fair password';
    } else if (score <= 4) {
        container.classList.add('strength-good');
        strengthText.textContent = 'Good password';
    } else {
        container.classList.add('strength-strong');
        strengthText.textContent = 'Strong password';
    }
}

function validatePasswordConfirmation(password, confirmPassword, field) {
    clearFieldError(field);
    
    if (confirmPassword && password !== confirmPassword) {
        showFieldError(field, 'Passwords do not match');
        return false;
    }
    
    return true;
}

// Add smooth transitions for form elements
const additionalStyles = `
    .form-input {
        transition: all 0.3s ease;
    }
    
    .form-input.is-invalid {
        border-color: #dc3545;
        box-shadow: 0 0 0 3px rgba(220, 53, 69, 0.1);
    }
    
    .field-error {
        animation: slideInDown 0.3s ease;
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .btn:disabled {
        opacity: 0.7;
        cursor: not-allowed;
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);