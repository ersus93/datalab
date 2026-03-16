/**
 * Módulo de búsqueda dinámica
 * Maneja la funcionalidad del modal de búsqueda
 */
class SearchModal {
    constructor() {
        this.modal = null;
        this.searchInput = null;
        this.resultsContainer = null;
        this.suggestionsContainer = null;
        this.searchTimeout = null;
        this.autocompleteTimeout = null;
        this.currentSuggestions = [];
        this.selectedIndex = -1;
        this.initialized = false;
        this.filters = {
            dateFrom: '',
            dateTo: '',
            area: '',
            entities: []
        };
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
        this.suggestionsContainer = this.modal.querySelector('#autocomplete-suggestions');
        this.closeButton = this.modal.querySelector('[data-modal-close]');
        this.recentSearchesContainer = this.modal.querySelector('#recent-searches-container');
        this.recentSearchesList = this.modal.querySelector('#recent-searches-list');
        this.searchResultsContent = this.modal.querySelector('#search-results-content');
        
        // Filter elements
        this.filterToggleBtn = this.modal.querySelector('#filter-toggle-btn');
        this.filterPanel = this.modal.querySelector('#filter-panel');
        this.dateFromInput = this.modal.querySelector('#filter-date-from');
        this.dateToInput = this.modal.querySelector('#filter-date-to');
        this.areaSelect = this.modal.querySelector('#filter-area');
        this.entityCheckboxes = this.modal.querySelectorAll('[id^="filter-entity-"]');
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
            this.searchInput.addEventListener('keydown', (e) => this.handleInputKeydown(e));
        }
        
        // Configurar evento para el botón de cierre
        document.addEventListener('click', (e) => {
            const closeButton = e.target.closest('[data-modal-close]');
            if (closeButton && closeButton.closest('#search-modal')) {
                e.preventDefault();
                this.close();
            }
        });

        // Filter toggle button
        if (this.filterToggleBtn) {
            this.filterToggleBtn.addEventListener('click', () => this.toggleFilterPanel());
        }

        // Filter inputs - persist filters between searches
        if (this.dateFromInput) {
            this.dateFromInput.addEventListener('change', () => {
                this.filters.dateFrom = this.dateFromInput.value;
                this.triggerSearchIfQueryExists();
            });
        }

        if (this.dateToInput) {
            this.dateToInput.addEventListener('change', () => {
                this.filters.dateTo = this.dateToInput.value;
                this.triggerSearchIfQueryExists();
            });
        }

        if (this.areaSelect) {
            this.areaSelect.addEventListener('change', () => {
                this.filters.area = this.areaSelect.value;
                this.triggerSearchIfQueryExists();
            });
        }

        if (this.entityCheckboxes) {
            this.entityCheckboxes.forEach(checkbox => {
                checkbox.addEventListener('change', () => {
                    this.filters.entities = Array.from(this.entityCheckboxes)
                        .filter(cb => cb.checked)
                        .map(cb => cb.value);
                    this.triggerSearchIfQueryExists();
                });
            });
        }

        // Cerrar sugerencias al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (this.suggestionsContainer && !this.suggestionsContainer.contains(e.target) && 
                e.target !== this.searchInput) {
                this.hideSuggestions();
            }
        });
    }

    /**
     * Triggea la búsqueda si hay una query existente
     */
    triggerSearchIfQueryExists() {
        if (this.searchInput && this.searchInput.value.trim()) {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.performSearch(this.searchInput.value.trim());
            }, 300);
        }
    }

    /**
     * Alterna el panel de filtros
     */
    toggleFilterPanel() {
        if (!this.filterPanel || !this.filterToggleBtn) return;

        const isExpanded = this.filterPanel.classList.contains('show');
        
        if (isExpanded) {
            this.filterPanel.classList.remove('show');
            this.filterToggleBtn.classList.remove('active');
            this.filterToggleBtn.setAttribute('aria-expanded', 'false');
        } else {
            this.filterPanel.classList.add('show');
            this.filterToggleBtn.classList.add('active');
            this.filterToggleBtn.setAttribute('aria-expanded', 'true');
        }
    }

    /**
     * Restaura los filtros guardados en los elementos del DOM
     */
    restoreFilters() {
        if (this.dateFromInput) {
            this.dateFromInput.value = this.filters.dateFrom;
        }
        if (this.dateToInput) {
            this.dateToInput.value = this.filters.dateTo;
        }
        if (this.areaSelect) {
            this.areaSelect.value = this.filters.area;
        }
        if (this.entityCheckboxes) {
            this.entityCheckboxes.forEach(checkbox => {
                checkbox.checked = this.filters.entities.includes(checkbox.value);
            });
        }
    }

    /**
     * Construye los parámetros de filtro para la URL
     */
    buildFilterParams() {
        const params = new URLSearchParams();

        if (this.filters.dateFrom) {
            params.append('date_from', this.filters.dateFrom);
        }
        if (this.filters.dateTo) {
            params.append('date_to', this.filters.dateTo);
        }
        if (this.filters.area) {
            params.append('area', this.filters.area);
        }
        if (this.filters.entities && this.filters.entities.length > 0) {
            params.append('entities', this.filters.entities.join(','));
        }

        return params.toString();
    }

    /**
     * Maneja el evento de entrada en el campo de búsqueda
     */
    handleSearchInput(e) {
        clearTimeout(this.searchTimeout);
        clearTimeout(this.autocompleteTimeout);
        const query = e.target.value.trim();
        
        // Resetear selección
        this.selectedIndex = -1;
        
        if (!query) {
            this.hideSuggestions();
            this.loadRecentSearches();
            return;
        }

        // Ocultar búsquedas recientes cuando hay query
        this.hideRecentSearches();

        // Autocomplete con debounce más corto (150ms)
        this.autocompleteTimeout = setTimeout(() => {
            this.fetchSuggestions(query);
        }, 150);

        // Búsqueda con debounce normal (300ms)
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, 300);
    }

    /**
     * Maneja los eventos de teclado en el input
     */
    handleInputKeydown(e) {
        if (this.currentSuggestions.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.selectedIndex = Math.min(this.selectedIndex + 1, this.currentSuggestions.length - 1);
            this.updateSelectedSuggestion();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
            this.updateSelectedSuggestion();
        } else if (e.key === 'Enter') {
            if (this.selectedIndex >= 0 && this.selectedIndex < this.currentSuggestions.length) {
                e.preventDefault();
                this.selectSuggestion(this.currentSuggestions[this.selectedIndex]);
            }
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
        }
    }

    /**
     * Actualiza la sugerencia seleccionada visualmente
     */
    updateSelectedSuggestion() {
        if (!this.suggestionsContainer) return;
        
        const items = this.suggestionsContainer.querySelectorAll('.autocomplete-suggestion');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }

    /**
     * Obtiene sugerencias del servidor
     */
    async fetchSuggestions(query) {
        if (!query || query.length < 2) {
            this.hideSuggestions();
            return;
        }

        try {
            const response = await fetch(`/api/search/autocomplete?q=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();
            
            if (data.suggestions && data.suggestions.length > 0) {
                this.currentSuggestions = data.suggestions;
                this.displaySuggestions(data.suggestions);
            } else {
                this.hideSuggestions();
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.hideSuggestions();
        }
    }

    /**
     * Muestra las sugerencias en el dropdown
     */
    displaySuggestions(suggestions) {
        if (!this.suggestionsContainer) return;

        this.suggestionsContainer.innerHTML = suggestions
            .map((suggestion, index) => `
                <div class="autocomplete-suggestion" data-index="${index}" data-value="${suggestion.text || suggestion.label || ''}">
                    ${suggestion.icon ? `<span class="autocomplete-icon">${suggestion.icon}</span>` : ''}
                    <span class="autocomplete-text">${suggestion.text || suggestion.label || suggestion}</span>
                    ${suggestion.type ? `<span class="autocomplete-type">${suggestion.type}</span>` : ''}
                </div>
            `)
            .join('');

        this.suggestionsContainer.style.display = 'block';

        // Agregar event listeners a las sugerencias
        this.suggestionsContainer.querySelectorAll('.autocomplete-suggestion').forEach(item => {
            item.addEventListener('click', (e) => {
                const value = item.getAttribute('data-value');
                this.selectSuggestion(value);
            });
            
            item.addEventListener('mouseenter', () => {
                this.selectedIndex = parseInt(item.getAttribute('data-index'));
                this.updateSelectedSuggestion();
            });
        });
    }

    /**
     * Selecciona una sugerencia
     */
    selectSuggestion(value) {
        if (!this.searchInput) return;
        
        this.searchInput.value = value;
        this.hideSuggestions();
        
        // Trigger search
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.performSearch(value);
        }, 150);
    }

    /**
     * Oculta las sugerencias
     */
    hideSuggestions() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.style.display = 'none';
            this.suggestionsContainer.innerHTML = '';
        }
        this.currentSuggestions = [];
        this.selectedIndex = -1;
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

            // Construir URL con filtros
            const filterParams = this.buildFilterParams();
            const url = `/api/search?q=${encodeURIComponent(query)}${filterParams ? '&' + filterParams : ''}`;

            // Llamar a la API de búsqueda
            const response = await fetch(url);
            const data = await response.json();
            
            // Verificar si results es un objeto (categorizado) o un array
            let flatResults = [];
            if (data.results) {
                if (Array.isArray(data.results)) {
                    // Es un array, usar directamente
                    flatResults = data.results;
                } else if (typeof data.results === 'object') {
                    // Es un objeto categorizado, flattenearlo
                    Object.entries(data.results).forEach(([category, items]) => {
                        if (Array.isArray(items)) {
                            items.forEach(item => {
                                flatResults.push({
                                    ...item,
                                    type: category
                                });
                            });
                        }
                    });
                }
            }
            
            if (flatResults.length > 0) {
                this.displayResults(flatResults);
                // Guardar la búsqueda reciente
                this.saveRecentSearch(query);
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
        this.hideRecentSearches();
        
        if (!this.searchResultsContent) return;

        const typeLabels = {
            clientes: 'Cliente',
            fabricas: 'Fábrica',
            productos: 'Producto',
            proveedores: 'Proveedor',
            pedidos: 'Pedido',
            usuarios: 'Usuario',
           Default: 'Resultado'
        };

        this.searchResultsContent.innerHTML = results
            .map(result => {
                const typeLabel = typeLabels[result.type] || typeLabels['Default'];
                return `
                    <div class="search-result-item" data-url="${result.url || '#'}">
                        <span class="search-result-badge" style="
                            display: inline-block;
                            padding: 2px 8px;
                            font-size: 11px;
                            font-weight: 600;
                            text-transform: uppercase;
                            border-radius: 3px;
                            margin-right: 8px;
                            background-color: #e3f2fd;
                            color: #1976d2;
                        ">${typeLabel}</span>
                        <div class="search-result-content" style="display: inline-block; vertical-align: middle;">
                            <div class="search-result-title">${result.title || 'Sin título'}</div>
                            ${result.description ? `<div class="search-result-description">${result.description}</div>` : ''}
                        </div>
                    </div>
                `;
            })
            .join('');

        this.searchResultsContent.style.display = 'block';

        // Agregar event listeners a los resultados
        this.searchResultsContent.querySelectorAll('.search-result-item').forEach(item => {
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
        this.hideRecentSearches();
        
        if (!this.searchResultsContent) return;
        this.searchResultsContent.innerHTML = `
            <div class="search-loading">
                <div class="spinner"></div>
                <p>Buscando...</p>
            </div>
        `;
        this.searchResultsContent.style.display = 'block';
    }

    /**
     * Carga las búsquedas recientes del servidor
     */
    async loadRecentSearches() {
        try {
            const response = await fetch('/api/search/recent?limit=10');
            const data = await response.json();
            
            if (data.searches && data.searches.length > 0) {
                this.displayRecentSearches(data.searches);
            } else {
                this.showEmptyState('Escribe para buscar...');
            }
        } catch (error) {
            console.error('Error loading recent searches:', error);
            this.showEmptyState('Escribe para buscar...');
        }
    }

    /**
     * Muestra las búsquedas recientes en el modal
     */
    displayRecentSearches(searches) {
        if (!this.recentSearchesContainer || !this.recentSearchesList || !this.searchResultsContent) return;

        this.recentSearchesList.innerHTML = searches
            .map(search => `
                <div class="recent-search-item" data-query="${search.query}">
                    <svg class="recent-search-item__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class="recent-search-item__text">${search.query}</span>
                    <button type="button" class="recent-search-item__delete" data-id="${search.id}" aria-label="Eliminar búsqueda">
                        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
            `)
            .join('');

        // Agregar event listeners
        this.recentSearchesList.querySelectorAll('.recent-search-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (e.target.closest('.recent-search-item__delete')) return;
                const query = item.getAttribute('data-query');
                if (this.searchInput) {
                    this.searchInput.value = query;
                }
                this.performSearch(query);
            });
        });

        this.recentSearchesList.querySelectorAll('.recent-search-item__delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const id = btn.getAttribute('data-id');
                this.deleteRecentSearch(id);
            });
        });

        this.recentSearchesContainer.style.display = 'block';
        this.searchResultsContent.style.display = 'none';
    }

    /**
     * Guarda una búsqueda reciente
     */
    async saveRecentSearch(query) {
        if (!query || !query.trim()) return;

        try {
            await fetch('/api/search/recent', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query.trim() })
            });
        } catch (error) {
            console.error('Error saving recent search:', error);
        }
    }

    /**
     * Elimina una búsqueda reciente
     */
    async deleteRecentSearch(id) {
        try {
            await fetch(`/api/search/recent/${id}`, {
                method: 'DELETE'
            });
            this.loadRecentSearches();
        } catch (error) {
            console.error('Error deleting recent search:', error);
        }
    }

    /**
     * Oculta las búsquedas recientes
     */
    hideRecentSearches() {
        if (this.recentSearchesContainer) {
            this.recentSearchesContainer.style.display = 'none';
        }
        if (this.searchResultsContent) {
            this.searchResultsContent.style.display = 'block';
        }
    }

    /**
     * Muestra el estado vacío con un mensaje
     */
    showEmptyState(message = 'Escribe para buscar...') {
        this.hideRecentSearches();
        
        if (!this.searchResultsContent) return;
        this.searchResultsContent.innerHTML = `
            <div class="search-modal__empty">
                <p>${message}</p>
            </div>
        `;
        this.searchResultsContent.style.display = 'block';
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
            
            // Restaurar filtros guardados
            this.restoreFilters();
            
            // Mostrar búsquedas recientes si no hay query
            this.loadRecentSearches();
            
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