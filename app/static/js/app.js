/**
 * DataLab - Main Application JavaScript
 * Handles core functionality, theme switching, dropdowns, and UI interactions
 */

// Global app object
const DataLab = {
    // Configuration
    config: {
        theme: localStorage.getItem('datalab-theme') || 'light',
        animations: !window.matchMedia('(prefers-reduced-motion: reduce)').matches
    },

    // Initialize the application
    init() {
        this.setupTheme();
        this.setupDropdowns();
        this.setupAlerts();
        this.setupMobileMenu();
        this.setupLoadingStates();
        this.setupToasts();
        this.setupModals();
        this.setupAccessibility();
        
        console.log('DataLab initialized successfully');
    },

    // Theme Management
    setupTheme() {
        const themeToggle = document.getElementById('theme-toggle');
        const html = document.documentElement;
        
        // Apply saved theme
        html.setAttribute('data-theme', this.config.theme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'light' ? 'dark' : 'light';
                
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('datalab-theme', newTheme);
                this.config.theme = newTheme;
                
                // Update icon
                this.updateThemeIcon(themeToggle, newTheme);
            });
            
            // Set initial icon
            this.updateThemeIcon(themeToggle, this.config.theme);
        }
    },

    updateThemeIcon(button, theme) {
        const icon = button.querySelector('svg');
        if (!icon) return;
        
        if (theme === 'dark') {
            icon.innerHTML = `
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            `;
        } else {
            icon.innerHTML = `
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            `;
        }
    },

    // Dropdown Management
    setupDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');
        
        dropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.dropdown__trigger');
            const menu = dropdown.querySelector('.dropdown__menu');
            
            if (!trigger || !menu) return;
            
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                const isOpen = trigger.getAttribute('aria-expanded') === 'true';
                
                // Close all other dropdowns
                this.closeAllDropdowns();
                
                if (!isOpen) {
                    this.openDropdown(dropdown, trigger, menu);
                }
            });
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });
        
        // Close dropdowns on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllDropdowns();
            }
        });
    },

    openDropdown(dropdown, trigger, menu) {
        trigger.setAttribute('aria-expanded', 'true');
        dropdown.classList.add('dropdown--open');
        menu.style.display = 'block';
        
        // Focus first menu item
        const firstItem = menu.querySelector('.dropdown__item');
        if (firstItem) {
            setTimeout(() => firstItem.focus(), 100);
        }
    },

    closeAllDropdowns() {
        const openDropdowns = document.querySelectorAll('.dropdown--open');
        
        openDropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.dropdown__trigger');
            const menu = dropdown.querySelector('.dropdown__menu');
            
            if (trigger) trigger.setAttribute('aria-expanded', 'false');
            dropdown.classList.remove('dropdown--open');
            if (menu) menu.style.display = 'none';
        });
    },

    // Alert Management
    setupAlerts() {
        const alerts = document.querySelectorAll('.alert--dismissible');
        
        alerts.forEach(alert => {
            const closeBtn = alert.querySelector('.alert__close');
            
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    this.dismissAlert(alert);
                });
            }
        });
    },

    dismissAlert(alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
            alert.remove();
        }, 300);
    },

    // Mobile Menu
    setupMobileMenu() {
        const mobileToggle = document.querySelector('.header__mobile-toggle');
        const nav = document.querySelector('.header__nav');
        
        if (mobileToggle && nav) {
            mobileToggle.addEventListener('click', () => {
                const isOpen = mobileToggle.getAttribute('aria-expanded') === 'true';
                
                mobileToggle.setAttribute('aria-expanded', !isOpen);
                nav.classList.toggle('header__nav--open', !isOpen);
                mobileToggle.classList.toggle('header__mobile-toggle--open', !isOpen);
                
                // Prevent body scroll when menu is open
                document.body.classList.toggle('menu-open', !isOpen);
            });
        }
    },

    // Loading States
    setupLoadingStates() {
        // Show loading overlay
        this.showLoading = (message = 'Cargando...') => {
            const overlay = document.getElementById('loading-overlay');
            const text = overlay?.querySelector('.loading-text');
            
            if (overlay) {
                if (text) text.textContent = message;
                overlay.style.display = 'flex';
            }
        };
        
        // Hide loading overlay
        this.hideLoading = () => {
            const overlay = document.getElementById('loading-overlay');
            if (overlay) {
                overlay.style.display = 'none';
            }
        };
    },

    // Toast Notifications
    setupToasts() {
        this.showToast = (message, type = 'info', duration = 5000) => {
            const container = document.getElementById('toast-container');
            if (!container) return;
            
            const toast = document.createElement('div');
            toast.className = `toast toast--${type}`;
            toast.innerHTML = `
                <div class="toast__content">
                    <span class="toast__message">${message}</span>
                    <button class="toast__close" aria-label="Cerrar notificación">
                        <svg class="icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            `;
            
            // Add close functionality
            const closeBtn = toast.querySelector('.toast__close');
            closeBtn.addEventListener('click', () => {
                this.removeToast(toast);
            });
            
            // Add to container
            container.appendChild(toast);
            
            // Show with animation
            setTimeout(() => {
                toast.classList.add('toast--show');
            }, 100);
            
            // Auto remove
            if (duration > 0) {
                setTimeout(() => {
                    this.removeToast(toast);
                }, duration);
            }
        };
        
        this.removeToast = (toast) => {
            toast.classList.remove('toast--show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        };
    },

    // Modal Management
    setupModals() {
        this.showModal = (content, options = {}) => {
            const container = document.getElementById('modal-container');
            if (!container) return;
            
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal__backdrop"></div>
                <div class="modal__content">
                    <div class="modal__header">
                        <h3 class="modal__title">${options.title || 'Modal'}</h3>
                        <button class="modal__close" aria-label="Cerrar modal">
                            <svg class="icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    <div class="modal__body">
                        ${content}
                    </div>
                </div>
            `;
            
            // Add close functionality
            const closeBtn = modal.querySelector('.modal__close');
            const backdrop = modal.querySelector('.modal__backdrop');
            
            const closeModal = () => {
                modal.classList.remove('modal--show');
                document.body.classList.remove('modal-open');
                setTimeout(() => {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                }, 300);
            };
            
            closeBtn.addEventListener('click', closeModal);
            backdrop.addEventListener('click', closeModal);
            
            // ESC key to close
            const handleEscape = (e) => {
                if (e.key === 'Escape') {
                    closeModal();
                    document.removeEventListener('keydown', handleEscape);
                }
            };
            document.addEventListener('keydown', handleEscape);
            
            // Add to container and show
            container.appendChild(modal);
            document.body.classList.add('modal-open');
            
            setTimeout(() => {
                modal.classList.add('modal--show');
            }, 100);
        };
    },

    // Accessibility Enhancements
    setupAccessibility() {
        // Skip link functionality
        const skipLink = document.querySelector('.skip-link');
        if (skipLink) {
            skipLink.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(skipLink.getAttribute('href'));
                if (target) {
                    target.focus();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        }
        
        // Focus management for keyboard navigation
        document.addEventListener('keydown', (e) => {
            // Tab trapping in modals
            if (e.key === 'Tab') {
                const modal = document.querySelector('.modal--show');
                if (modal) {
                    this.trapFocus(e, modal);
                }
            }
        });
    },

    trapFocus(e, container) {
        const focusableElements = container.querySelectorAll(
            'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];
        
        if (e.shiftKey) {
            if (document.activeElement === firstElement) {
                lastElement.focus();
                e.preventDefault();
            }
        } else {
            if (document.activeElement === lastElement) {
                firstElement.focus();
                e.preventDefault();
            }
        }
    },

    // Utility Functions
    utils: {
        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Format date
        formatDate(date, options = {}) {
            return new Intl.DateTimeFormat('es-ES', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                ...options
            }).format(new Date(date));
        },
        
        // Format number
        formatNumber(number, options = {}) {
            return new Intl.NumberFormat('es-ES', options).format(number);
        }
    }
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => DataLab.init());
} else {
    DataLab.init();
}

// Export for global access
window.DataLab = DataLab;