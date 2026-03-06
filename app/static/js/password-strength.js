/**
 * Password Strength Indicator
 * Calculates and displays password strength visually
 */

(function() {
    'use strict';
    
    function calculateStrength(password) {
        let score = 0;
        
        if (!password) return { score: 0, level: 'none', text: '' };
        
        // Length checks
        if (password.length >= 8) score += 1;
        if (password.length >= 12) score += 1;
        if (password.length >= 16) score += 1;
        
        // Character type checks
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^a-zA-Z0-9]/.test(password)) score += 1;
        
        // Common patterns (penalty)
        if (/^(.)\1+$/.test(password)) score -= 1; // repeated chars
        if (/^(password|123456|qwerty)/i.test(password)) score = 0; // common passwords
        
        // Normalize to 0-100
        const maxScore = 8;
        const percentage = Math.max(0, Math.min(100, (score / maxScore) * 100));
        
        // Determine level
        let level, color, text;
        if (percentage < 25) {
            level = 'weak';
            color = '#dc3545'; // red
            text = 'Debil';
        } else if (percentage < 50) {
            level = 'fair';
            color = '#ffc107'; // yellow
            text = 'Regular';
        } else if (percentage < 75) {
            level = 'good';
            color = '#17a2b8'; // cyan
            text = 'Buena';
        } else {
            level = 'strong';
            color = '#28a745'; // green
            text = 'Fuerte';
        }
        
        return { score: percentage, level: level, color: color, text: text };
    }
    
    function updateStrengthMeter(password, meterId) {
        const meter = document.getElementById(meterId);
        if (!meter) return;
        
        const strength = calculateStrength(password);
        
        // Update bar
        meter.style.width = strength.score + '%';
        meter.style.backgroundColor = strength.color;
        meter.setAttribute('data-level', strength.level);
        
        // Update text
        const textEl = document.getElementById(meterId + '-text');
        if (textEl) {
            textEl.textContent = strength.text;
            textEl.style.color = strength.color;
        }
    }
    
    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        const passwordInput = document.getElementById('password');
        const confirmInput = document.getElementById('confirmar_password');
        
        if (passwordInput) {
            // Add strength meter HTML
            const meterContainer = document.createElement('div');
            meterContainer.className = 'password-strength mt-2';
            meterContainer.innerHTML = `
                <div class="progress" style="height: 8px;">
                    <div id="password-strength-bar" class="progress-bar" 
                         role="progressbar" style="width: 0%"></div>
                </div>
                <small id="password-strength-bar-text" class="text-muted"></small>
            `;
            passwordInput.parentNode.appendChild(meterContainer);
            
            // Add event listener
            passwordInput.addEventListener('input', function() {
                updateStrengthMeter(this.value, 'password-strength-bar');
            });
        }
        
        // Match indicator
        if (confirmInput && passwordInput) {
            confirmInput.addEventListener('input', function() {
                const matchEl = document.getElementById('password-match');
                if (!matchEl) {
                    const el = document.createElement('small');
                    el.id = 'password-match';
                    el.className = 'd-block mt-1';
                    confirmInput.parentNode.appendChild(el);
                }
                
                const match = document.getElementById('password-match');
                if (this.value && this.value === passwordInput.value) {
                    match.textContent = '✓ Las contrasenas coinciden';
                    match.className = 'd-block mt-1 text-success';
                } else if (this.value) {
                    match.textContent = '✗ Las contrasenas no coinciden';
                    match.className = 'd-block mt-1 text-danger';
                }
            });
        }
    });
})();