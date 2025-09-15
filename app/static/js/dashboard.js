/**
 * Dashboard JavaScript - Modern UX/UI Enhancements
 * Provides smooth animations, interactive components, and enhanced user experience
 */

// Dashboard Application Class
class DashboardApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeAnimations();
        this.setupThemeToggle();
        this.setupSidebar();
        this.setupUserDropdown();
        this.setupFlashMessages();
        this.setupMetricCards();
        this.setupLoadingStates();
        this.initializeTooltips();
    }

    // Event Listeners Setup
    setupEventListeners() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.fadeInElements();
        });

        // Window Resize
        window.addEventListener('resize', this.debounce(() => {
            this.handleResize();
        }, 250));

        // Scroll Events
        window.addEventListener('scroll', this.throttle(() => {
            this.handleScroll();
        }, 16));
    }

    // Initialize Page Animations
    initializeAnimations() {
        // Animate elements on page load
        const animatedElements = document.querySelectorAll('.metric-card, .dashboard-card, .activity-item');
        
        animatedElements.forEach((element, index) => {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    // Fade in elements
    fadeInElements() {
        const elements = document.querySelectorAll('.animate-fade-in');
        elements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('visible');
            }, index * 150);
        });
    }

    // Theme Toggle Functionality
    setupThemeToggle() {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) return;

        // Get current theme from localStorage or default to light
        const currentTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', currentTheme);
        this.updateThemeIcon(currentTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Add transition class for smooth theme change
            document.documentElement.classList.add('theme-transitioning');
            
            setTimeout(() => {
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                this.updateThemeIcon(newTheme);
                
                setTimeout(() => {
                    document.documentElement.classList.remove('theme-transitioning');
                }, 300);
            }, 50);
        });
    }

    updateThemeIcon(theme) {
        const themeToggle = document.querySelector('.theme-toggle');
        if (!themeToggle) return;

        const icon = themeToggle.querySelector('svg');
        if (theme === 'dark') {
            icon.innerHTML = `
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
            `;
        } else {
            icon.innerHTML = `
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
            `;
        }
    }

    // Sidebar Functionality
    setupSidebar() {
        const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.createElement('div');
        overlay.className = 'sidebar-overlay';
        document.body.appendChild(overlay);

        if (!mobileMenuToggle || !sidebar) return;

        // Mobile menu toggle
        mobileMenuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
            overlay.classList.toggle('active');
            document.body.classList.toggle('sidebar-open');
        });

        // Close sidebar when clicking overlay
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('mobile-open');
            overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        });

        // Close sidebar on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
                sidebar.classList.remove('mobile-open');
                overlay.classList.remove('active');
                document.body.classList.remove('sidebar-open');
            }
        });

        // Highlight active navigation item
        const navItems = document.querySelectorAll('.sidebar-nav-item');
        const currentPath = window.location.pathname;
        
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href && (currentPath === href || currentPath.startsWith(href + '/'))) {
                item.classList.add('active');
            }
        });
    }

    // User Dropdown Functionality
    setupUserDropdown() {
        const userDropdown = document.querySelector('.user-dropdown');
        if (!userDropdown) return;

        const trigger = userDropdown.querySelector('.user-dropdown-trigger');
        const menu = userDropdown.querySelector('.user-dropdown-menu');

        if (!trigger || !menu) return;

        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userDropdown.contains(e.target)) {
                userDropdown.classList.remove('active');
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                userDropdown.classList.remove('active');
            }
        });
    }

    // Flash Messages Functionality
    setupFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');
        
        flashMessages.forEach(message => {
            const dismissBtn = message.querySelector('.flash-dismiss');
            if (dismissBtn) {
                dismissBtn.addEventListener('click', () => {
                    this.dismissFlashMessage(message);
                });
            }

            // Auto-dismiss after 5 seconds for success messages
            if (message.classList.contains('flash-success')) {
                setTimeout(() => {
                    this.dismissFlashMessage(message);
                }, 5000);
            }
        });
    }

    dismissFlashMessage(message) {
        message.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
        message.style.opacity = '0';
        message.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            message.remove();
        }, 300);
    }

    // Metric Cards Enhancements
    setupMetricCards() {
        const metricCards = document.querySelectorAll('.metric-card');
        
        metricCards.forEach(card => {
            // Add hover effect
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-4px)';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });

            // Animate metric values on scroll into view
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateMetricValue(entry.target);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(card);
        });
    }

    animateMetricValue(card) {
        const valueElement = card.querySelector('.metric-value');
        if (!valueElement) return;

        const finalValue = valueElement.textContent;
        const numericValue = parseFloat(finalValue.replace(/[^0-9.-]+/g, ''));
        
        if (isNaN(numericValue)) return;

        let currentValue = 0;
        const increment = numericValue / 60; // 60 frames for 1 second animation
        const suffix = finalValue.replace(/[0-9.-]+/g, '');

        const animate = () => {
            currentValue += increment;
            if (currentValue >= numericValue) {
                valueElement.textContent = finalValue;
                return;
            }
            
            valueElement.textContent = Math.floor(currentValue) + suffix;
            requestAnimationFrame(animate);
        };

        animate();
    }

    // Loading States
    setupLoadingStates() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        
        // Show loading overlay for form submissions
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', () => {
                this.showLoading();
            });
        });

        // Show loading for navigation links
        const navLinks = document.querySelectorAll('a[href]:not([href^="#"]):not([href^="javascript:"])');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                if (!e.ctrlKey && !e.metaKey) {
                    setTimeout(() => this.showLoading(), 100);
                }
            });
        });
    }

    showLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.add('active');
        }
    }

    hideLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
    }

    // Initialize Tooltips
    initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });

            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element) {
        const tooltipText = element.getAttribute('data-tooltip');
        if (!tooltipText) return;

        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = tooltipText;
        tooltip.id = 'active-tooltip';
        
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';

        setTimeout(() => {
            tooltip.classList.add('visible');
        }, 10);
    }

    hideTooltip() {
        const tooltip = document.getElementById('active-tooltip');
        if (tooltip) {
            tooltip.classList.remove('visible');
            setTimeout(() => {
                tooltip.remove();
            }, 200);
        }
    }

    // Handle Window Resize
    handleResize() {
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (window.innerWidth > 768) {
            if (sidebar) sidebar.classList.remove('mobile-open');
            if (overlay) overlay.classList.remove('active');
            document.body.classList.remove('sidebar-open');
        }
    }

    // Handle Scroll Events
    handleScroll() {
        const header = document.querySelector('.header');
        if (!header) return;

        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }

    // Utility Functions
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
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Public API Methods
    refreshMetrics() {
        const metricCards = document.querySelectorAll('.metric-card');
        metricCards.forEach(card => {
            this.animateMetricValue(card);
        });
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `flash-message flash-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="flash-dismiss" type="button">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;

        const container = document.querySelector('.flash-messages') || document.querySelector('.content-container');
        if (container) {
            container.insertBefore(notification, container.firstChild);
            
            // Setup dismiss functionality
            const dismissBtn = notification.querySelector('.flash-dismiss');
            if (dismissBtn) {
                dismissBtn.addEventListener('click', () => {
                    this.dismissFlashMessage(notification);
                });
            }

            // Auto-dismiss
            if (type === 'success') {
                setTimeout(() => {
                    this.dismissFlashMessage(notification);
                }, 5000);
            }
        }
    }
}

// Initialize Dashboard App
const dashboardApp = new DashboardApp();

// Export for global access
window.DashboardApp = dashboardApp;

// Additional CSS for enhanced animations and effects
const additionalStyles = `
    .theme-transitioning * {
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
    }
    
    .sidebar-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1025;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease;
    }
    
    .sidebar-overlay.active {
        opacity: 1;
        visibility: visible;
    }
    
    .header.scrolled {
        box-shadow: var(--shadow-md);
    }
    
    .tooltip {
        position: absolute;
        background: var(--secondary-900);
        color: white;
        padding: var(--spacing-2) var(--spacing-3);
        border-radius: var(--radius-md);
        font-size: var(--font-size-xs);
        z-index: var(--z-tooltip);
        opacity: 0;
        transform: translateY(4px);
        transition: opacity 0.2s ease, transform 0.2s ease;
        pointer-events: none;
        white-space: nowrap;
    }
    
    .tooltip.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    .tooltip::after {
        content: '';
        position: absolute;
        top: 100%;
        left: 50%;
        transform: translateX(-50%);
        border: 4px solid transparent;
        border-top-color: var(--secondary-900);
    }
    
    .animate-fade-in {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease-out, transform 0.6s ease-out;
    }
    
    .animate-fade-in.visible {
        opacity: 1;
        transform: translateY(0);
    }
    
    @media (max-width: 768px) {
        .sidebar-overlay {
            display: block;
        }
        
        body.sidebar-open {
            overflow: hidden;
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);