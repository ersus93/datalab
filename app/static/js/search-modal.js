/**
 * Módulo de búsqueda dinámica
 * Maneja la funcionalidad del modal de búsqueda
 */
class SearchModal {
    constructor() {
        this.modal = null;
        this.searchInput = null;
        this.resultsContainer = null;
        this.searchTimeout = null;
        this.initialized = false;
    }

    /**
     * Inicializa el modal de búsqueda
     */
    init() {
        if (this.initialized) return;

        // Cargar el template del modal si no existe
        if (!document.getElementById('search-modal')) {
            this.loadModalTemplate();
        }

        this.cacheElements();
        this.setupEventListeners();
        this.initialized = true;
    }

    /**
     * Carga el template del modal desde el servidor
     */
    loadModalTemplate() {
        // El modal se carga directamente desde el template HTML
        // usando la ruta correcta del componente
    }

    /**
     * Cachea los elementos del DOM necesarios
     */
    cacheElements() {
        this.modal = document.getElementById('search-modal');
        if (!this.modal) return;

        this.searchInput = this.modal.querySelector('#search-modal-input');
        this.resultsContainer = this.modal.querySelector('#search-results');
        this.closeButton = this.modal.querySelector('[data-modal-close]');
    }

    /**
     * Configura los event listeners
     */
    setupEventListeners() {
        // Atajo de teclado Ctrl+K o Cmd+K para abrir el modal
        document.addEventListener('keydown', (e) => {
            // Solo activar si no hay un input o textarea activo
            if ((e.ctrlKey || e.metaKey) && e.key === 'k' && 
                !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
                e.preventDefault();
                this.open();
            }
        });

        // Configurar evento de búsqueda
        if (this.searchInput) {
            this.searchInput.addEventListener('input', (e) => this.handleSearchInput(e));
        }
        
        // Configurar evento para el botón de cierre
        document.addEventListener('click', (e) => {
            const closeButton = e.target.closest('[data-modal-close]');
            if (closeButton && closeButton.closest('#search-modal')) {
                e.preventDefault();
                this.close();
            }
        });
    }

    /**
     * Maneja el evento de entrada en el campo de búsqueda
     */
    handleSearchInput(e) {
        clearTimeout(this.searchTimeout);
        const query = e.target.value.trim();
        
        if (!query) {
            this.showEmptyState();
            return;
        }

        // Hacer la búsqueda después de una pequeña pausa (debounce)
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    /**
     * Realiza la búsqueda
     */
    async performSearch(query) {
        if (!query) {
            this.showEmptyState('Escribe para buscar...');
            return;
        }

        try {
            // Mostrar estado de carga
            this.showLoadingState();

            // Llamar a la API de búsqueda
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                this.displayResults(data.results);
            } else {
                this.showEmptyState('No se encontraron resultados');
            }
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            this.showEmptyState('Error al realizar la búsqueda');
        }
    }

    /**
     * Muestra los resultados de la búsqueda
     */
    displayResults(results) {
        if (!this.resultsContainer) return;

        this.resultsContainer.innerHTML = results
            .map(result => `
                <div class="search-result-item" data-url="${result.url || '#'}">
                    <div class="search-result-title">${result.title || 'Sin título'}</div>
                    ${result.description ? `<div class="search-result-description">${result.description}</div>` : ''}
                </div>
            `)
            .join('');

        // Agregar event listeners a los resultados
        this.resultsContainer.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const url = item.getAttribute('data-url');
                if (url && url !== '#') {
                    window.location.href = url;
                }
            });
        });
    }

    /**
     * Muestra el estado de carga
     */
    showLoadingState() {
        if (!this.resultsContainer) return;
        this.resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="spinner"></div>
                <p>Buscando...</p>
            </div>
        `;
    }

    /**
     * Muestra el estado vacío con un mensaje
     */
    showEmptyState(message = 'Escribe para buscar...') {
        if (!this.resultsContainer) return;
        this.resultsContainer.innerHTML = `
            <div class="search-modal__empty">
                <p>${message}</p>
            </div>
        `;
    }

    /**
     * Abre el modal de búsqueda
     */
    open() {
        this.cacheElements();
        
        if (!this.modal) {
            console.error('No se pudo encontrar el elemento del modal');
            return;
        }
        
        // Mostrar el modal
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Agregar clase para la animación
        setTimeout(() => {
            this.modal.classList.add('show');
            
            // Enfocar el input después de la animación
            if (this.searchInput) {
                this.searchInput.value = '';
                this.searchInput.focus();
            }
            
            // Mostrar estado inicial
            this.showEmptyState('Escribe para buscar...');
            
            // Configurar evento para cerrar al hacer clic fuera del modal
            this.modal.addEventListener('click', this.handleOutsideClick);
            
            // Configurar evento para cerrar con Escape
            document.addEventListener('keydown', this.handleEscapeKey);
        }, 10);
    }

    /**
     * Cierra el modal de búsqueda
     */
    close() {
        if (!this.modal) return;
        
        // Eliminar eventos
        this.modal.removeEventListener('click', this.handleOutsideClick);
        document.removeEventListener('keydown', this.handleEscapeKey);
        
        // Iniciar animación de cierre
        this.modal.classList.remove('show');
        
        // Ocultar después de la animación
        setTimeout(() => {
            this.modal.style.display = 'none';
            document.body.style.overflow = '';
        }, 200);
    }
    
    /**
     * Maneja el clic fuera del modal
     */
    handleOutsideClick = (e) => {
        if (e.target === this.modal) {
            this.close();
        }
    }
    
    /**
     * Maneja la tecla Escape para cerrar el modal
     */
    handleEscapeKey = (e) => {
        if (e.key === 'Escape') {
            this.close();
        }
    }
}

// Inicializar el módulo de búsqueda
DataLab.SearchModal = new SearchModal();

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        DataLab.SearchModal.init();
    });
} else {
    DataLab.SearchModal.init();
}

// Hacer la función accesible globalmente
DataLab.showSearchModal = () => DataLab.SearchModal.open();