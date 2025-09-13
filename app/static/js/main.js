/**
 * ONIE DataLab - Main JavaScript
 * Funcionalidades principales de la aplicación
 */

// === CONFIGURACIÓN GLOBAL ===
const DataLab = {
    config: {
        apiBaseUrl: '/api',
        chartColors: {
            primary: '#3B82F6',
            success: '#10B981',
            warning: '#F59E0B',
            danger: '#EF4444',
            info: '#06B6D4',
            secondary: '#6B7280'
        },
        animations: {
            duration: 300,
            easing: 'ease-out'
        }
    },
    
    // Estado global de la aplicación
    state: {
        sidebarCollapsed: false,
        currentTheme: 'light',
        activeModals: [],
        notifications: []
    },
    
    // Utilidades
    utils: {},
    
    // Componentes
    components: {},
    
    // Módulos
    modules: {}
};

// === UTILIDADES ===
DataLab.utils = {
    /**
     * Debounce function para optimizar eventos
     */
    debounce(func, wait, immediate) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                timeout = null;
                if (!immediate) func(...args);
            };
            const callNow = immediate && !timeout;
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
            if (callNow) func(...args);
        };
    },
    
    /**
     * Throttle function para limitar ejecuciones
     */
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    /**
     * Formatear números con separadores de miles
     */
    formatNumber(num, decimals = 0) {
        return new Intl.NumberFormat('es-ES', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },
    
    /**
     * Formatear fechas
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        };
        return new Intl.DateTimeFormat('es-ES', { ...defaultOptions, ...options }).format(new Date(date));
    },
    
    /**
     * Generar ID único
     */
    generateId() {
        return 'id_' + Math.random().toString(36).substr(2, 9);
    },
    
    /**
     * Validar email
     */
    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    /**
     * Escapar HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },
    
    /**
     * Hacer peticiones AJAX
     */
    async request(url, options = {}) {
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        };
        
        // Agregar CSRF token si existe
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken) {
            defaultOptions.headers['X-CSRFToken'] = csrfToken;
        }
        
        try {
            const response = await fetch(url, { ...defaultOptions, ...options });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return await response.text();
        } catch (error) {
            console.error('Request failed:', error);
            throw error;
        }
    }
};

// === COMPONENTES ===

/**
 * Componente de Sidebar
 */
DataLab.components.Sidebar = {
    init() {
        this.bindEvents();
        this.loadState();
    },
    
    bindEvents() {
        // Toggle sidebar
        const toggleBtn = document.querySelector('.navbar-toggler');
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener('click', () => {
                this.toggle();
            });
        }
        
        // Cerrar sidebar en móvil al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 1024) {
                if (!sidebar?.contains(e.target) && !toggleBtn?.contains(e.target)) {
                    this.hide();
                }
            }
        });
        
        // Responsive behavior
        window.addEventListener('resize', DataLab.utils.debounce(() => {
            this.handleResize();
        }, 250));
    },
    
    toggle() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (window.innerWidth <= 1024) {
            // Móvil: mostrar/ocultar
            sidebar?.classList.toggle('show');
        } else {
            // Desktop: colapsar/expandir
            sidebar?.classList.toggle('collapsed');
            mainContent?.classList.toggle('sidebar-collapsed');
            DataLab.state.sidebarCollapsed = sidebar?.classList.contains('collapsed');
            this.saveState();
        }
    },
    
    show() {
        const sidebar = document.querySelector('.sidebar');
        sidebar?.classList.add('show');
    },
    
    hide() {
        const sidebar = document.querySelector('.sidebar');
        sidebar?.classList.remove('show');
    },
    
    handleResize() {
        const sidebar = document.querySelector('.sidebar');
        const mainContent = document.querySelector('.main-content');
        
        if (window.innerWidth > 1024) {
            sidebar?.classList.remove('show');
            if (DataLab.state.sidebarCollapsed) {
                sidebar?.classList.add('collapsed');
                mainContent?.classList.add('sidebar-collapsed');
            }
        } else {
            sidebar?.classList.remove('collapsed');
            mainContent?.classList.remove('sidebar-collapsed');
        }
    },
    
    saveState() {
        localStorage.setItem('datalab_sidebar_collapsed', DataLab.state.sidebarCollapsed);
    },
    
    loadState() {
        const saved = localStorage.getItem('datalab_sidebar_collapsed');
        if (saved === 'true' && window.innerWidth > 1024) {
            DataLab.state.sidebarCollapsed = true;
            const sidebar = document.querySelector('.sidebar');
            const mainContent = document.querySelector('.main-content');
            sidebar?.classList.add('collapsed');
            mainContent?.classList.add('sidebar-collapsed');
        }
    }
};

/**
 * Componente de Notificaciones
 */
DataLab.components.Notifications = {
    init() {
        this.container = this.createContainer();
        this.bindEvents();
    },
    
    createContainer() {
        let container = document.querySelector('.flash-messages');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-messages';
            document.body.appendChild(container);
        }
        return container;
    },
    
    bindEvents() {
        // Auto-dismiss existing flash messages
        document.querySelectorAll('.alert[data-auto-dismiss]').forEach(alert => {
            const delay = parseInt(alert.dataset.autoDismiss) || 5000;
            setTimeout(() => {
                this.dismiss(alert);
            }, delay);
        });
        
        // Manual dismiss buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('.alert .btn-close')) {
                const alert = e.target.closest('.alert');
                this.dismiss(alert);
            }
        });
    },
    
    show(message, type = 'info', options = {}) {
        const id = DataLab.utils.generateId();
        const alert = document.createElement('div');
        
        const defaultOptions = {
            dismissible: true,
            autoDismiss: 5000,
            icon: true
        };
        
        const config = { ...defaultOptions, ...options };
        
        alert.className = `alert alert-${type} ${config.dismissible ? 'alert-dismissible' : ''}`;
        alert.setAttribute('role', 'alert');
        alert.setAttribute('data-alert-id', id);
        
        let iconHtml = '';
        if (config.icon) {
            const icons = {
                success: '✓',
                danger: '✕',
                warning: '⚠',
                info: 'ℹ'
            };
            iconHtml = `<span class="alert-icon">${icons[type] || icons.info}</span>`;
        }
        
        const closeBtn = config.dismissible ? 
            '<button type="button" class="btn-close" aria-label="Cerrar"><span aria-hidden="true">&times;</span></button>' : '';
        
        alert.innerHTML = `
            ${iconHtml}
            <span class="alert-message">${DataLab.utils.escapeHtml(message)}</span>
            ${closeBtn}
        `;
        
        this.container.appendChild(alert);
        
        // Auto dismiss
        if (config.autoDismiss) {
            setTimeout(() => {
                this.dismiss(alert);
            }, config.autoDismiss);
        }
        
        // Agregar al estado
        DataLab.state.notifications.push({ id, type, message, element: alert });
        
        return id;
    },
    
    dismiss(alertElement) {
        if (!alertElement) return;
        
        alertElement.style.animation = 'slideOutRight 0.3s ease-out';
        
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.parentNode.removeChild(alertElement);
            }
            
            // Remover del estado
            const id = alertElement.getAttribute('data-alert-id');
            DataLab.state.notifications = DataLab.state.notifications.filter(n => n.id !== id);
        }, 300);
    },
    
    clear() {
        const alerts = this.container.querySelectorAll('.alert');
        alerts.forEach(alert => this.dismiss(alert));
    }
};

/**
 * Componente de Modales
 */
DataLab.components.Modal = {
    init() {
        this.bindEvents();
    },
    
    bindEvents() {
        // Cerrar modal con ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAll();
            }
        });
        
        // Cerrar modal al hacer clic en el overlay
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.close(e.target.querySelector('.modal'));
            }
        });
        
        // Botones de cerrar modal
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-modal-close]')) {
                const modal = e.target.closest('.modal');
                this.close(modal);
            }
        });
    },
    
    open(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        const overlay = modal.closest('.modal-overlay') || this.createOverlay(modal);
        
        document.body.style.overflow = 'hidden';
        overlay.style.display = 'flex';
        
        // Focus management
        const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        }
        
        DataLab.state.activeModals.push(modalId);
    },
    
    close(modal) {
        if (!modal) return;
        
        const overlay = modal.closest('.modal-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
        
        const modalId = modal.id;
        DataLab.state.activeModals = DataLab.state.activeModals.filter(id => id !== modalId);
        
        if (DataLab.state.activeModals.length === 0) {
            document.body.style.overflow = '';
        }
    },
    
    closeAll() {
        const overlays = document.querySelectorAll('.modal-overlay');
        overlays.forEach(overlay => {
            overlay.style.display = 'none';
        });
        
        DataLab.state.activeModals = [];
        document.body.style.overflow = '';
    },
    
    createOverlay(modal) {
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.style.display = 'none';
        
        // Mover el modal al overlay
        modal.parentNode.removeChild(modal);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        return overlay;
    }
};

/**
 * Componente de Formularios
 */
DataLab.components.Forms = {
    init() {
        this.bindEvents();
        this.initValidation();
    },
    
    bindEvents() {
        // Auto-resize textareas
        document.addEventListener('input', (e) => {
            if (e.target.tagName === 'TEXTAREA' && e.target.classList.contains('auto-resize')) {
                this.autoResize(e.target);
            }
        });
        
        // Form submission con loading state
        document.addEventListener('submit', (e) => {
            const form = e.target;
            if (form.classList.contains('ajax-form')) {
                e.preventDefault();
                this.handleAjaxSubmit(form);
            }
        });
    },
    
    autoResize(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = textarea.scrollHeight + 'px';
    },
    
    async handleAjaxSubmit(form) {
        const submitBtn = form.querySelector('[type="submit"]');
        const originalText = submitBtn?.textContent;
        
        // Loading state
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Enviando...';
        }
        
        try {
            const formData = new FormData(form);
            const response = await DataLab.utils.request(form.action, {
                method: form.method || 'POST',
                body: formData
            });
            
            if (response.success) {
                DataLab.components.Notifications.show(response.message || 'Operación exitosa', 'success');
                if (response.redirect) {
                    window.location.href = response.redirect;
                }
            } else {
                DataLab.components.Notifications.show(response.message || 'Error en la operación', 'danger');
            }
        } catch (error) {
            DataLab.components.Notifications.show('Error de conexión', 'danger');
        } finally {
            // Restore button
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        }
    },
    
    initValidation() {
        // Validación en tiempo real
        document.addEventListener('blur', (e) => {
            if (e.target.matches('input, select, textarea')) {
                this.validateField(e.target);
            }
        }, true);
    },
    
    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        let message = '';
        
        // Required validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            message = 'Este campo es obligatorio';
        }
        
        // Email validation
        if (field.type === 'email' && value && !DataLab.utils.isValidEmail(value)) {
            isValid = false;
            message = 'Ingrese un email válido';
        }
        
        // Min length validation
        const minLength = field.getAttribute('minlength');
        if (minLength && value.length < parseInt(minLength)) {
            isValid = false;
            message = `Mínimo ${minLength} caracteres`;
        }
        
        this.showFieldValidation(field, isValid, message);
        return isValid;
    },
    
    showFieldValidation(field, isValid, message) {
        const container = field.closest('.form-group') || field.parentNode;
        let feedback = container.querySelector('.invalid-feedback');
        
        // Remove existing classes
        field.classList.remove('is-valid', 'is-invalid');
        
        if (!isValid) {
            field.classList.add('is-invalid');
            
            if (!feedback) {
                feedback = document.createElement('div');
                feedback.className = 'invalid-feedback';
                container.appendChild(feedback);
            }
            
            feedback.textContent = message;
        } else {
            field.classList.add('is-valid');
            if (feedback) {
                feedback.remove();
            }
        }
    }
};

// === INICIALIZACIÓN ===
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar componentes
    DataLab.components.Sidebar.init();
    DataLab.components.Notifications.init();
    DataLab.components.Modal.init();
    DataLab.components.Forms.init();
    
    // Configurar tooltips si existe la librería
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    }
    
    // Smooth scroll para enlaces internos
    document.addEventListener('click', (e) => {
        if (e.target.matches('a[href^="#"]')) {
            e.preventDefault();
            const target = document.querySelector(e.target.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });
    
    console.log('ONIE DataLab initialized successfully');
});

// Exponer DataLab globalmente
window.DataLab = DataLab;

// === ANIMACIONES CSS ADICIONALES ===
const additionalStyles = `
@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(100%);
        opacity: 0;
    }
}

.loading {
    position: relative;
    pointer-events: none;
}

.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    margin: -10px 0 0 -10px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid var(--color-primary);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
`;

// Agregar estilos adicionales
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);