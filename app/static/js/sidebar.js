/**
 * Sidebar Manager - Versión simplificada
 * Maneja únicamente el comportamiento básico del sidebar fijo
 */
class SidebarManager {
    constructor() {
        this.sidebar = null;
        this.overlay = null;
        this.init();
    }

    init() {
        // Esperar a que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Obtener elementos del DOM
        this.sidebar = document.getElementById('sidebar');
        this.overlay = document.getElementById('sidebar-overlay');

        if (!this.sidebar) {
            console.warn('Sidebar element not found');
            return;
        }

        // Configurar eventos para móvil
        this.setupMobileEvents();
        
        // Manejar redimensionamiento de ventana
        window.addEventListener('resize', () => this.handleResize());
        
        // Configuración inicial
        this.handleResize();
    }

    setupMobileEvents() {
        // Solo para dispositivos móviles - cerrar con overlay
        if (this.overlay) {
            this.overlay.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    this.closeMobileSidebar();
                }
            });
        }

        // Cerrar con tecla Escape en móvil
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && window.innerWidth <= 768) {
                this.closeMobileSidebar();
            }
        });
    }

    closeMobileSidebar() {
        if (this.sidebar) {
            this.sidebar.classList.remove('active');
        }
        if (this.overlay) {
            this.overlay.classList.remove('active');
        }
    }

    handleResize() {
        // En desktop, asegurar que el sidebar esté siempre visible
        if (window.innerWidth > 768) {
            if (this.sidebar) {
                this.sidebar.classList.remove('active');
            }
            if (this.overlay) {
                this.overlay.classList.remove('active');
            }
        }
    }
}

// Inicializar el sidebar manager
const sidebarManager = new SidebarManager();