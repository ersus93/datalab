/**
 * Módulo de búsqueda dinámica
 */
DataLab.SearchModal = {
    init() {
        this.searchResults = [];
        this.setupEventListeners();
    },

    setupEventListeners() {
        document.addEventListener('keydown', (e) => {
            // Atajo de teclado Ctrl+K o Cmd+K para abrir el modal
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                DataLab.showSearchModal();
            }
        });
    },

    async search(query) {
        if (!query.trim()) {
            this.searchResults = [];
            return;
        }

        try {
            // Aquí implementarías la llamada a tu API de búsqueda
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            this.searchResults = data.results;
        } catch (error) {
            console.error('Error en la búsqueda:', error);
            this.searchResults = [];
        }

        this.renderResults();
    },

    renderResults() {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;

        if (!this.searchResults.length) {
            resultsContainer.innerHTML = `
                <div class="search-modal__empty">
                    <p>No se encontraron resultados</p>
                </div>
            `;
            return;
        }

        resultsContainer.innerHTML = this.searchResults
            .map(result => `
                <div class="search-result-item" onclick="window.location.href='${result.url}'">
                    <div class="search-result-title">${result.title}</div>
                    <div class="search-result-description">${result.description}</div>
                </div>
            `)
            .join('');
    }
};

// Extender la funcionalidad del modal en DataLab
DataLab.showSearchModal = function() {
    const modalContent = `
        <div class="search-modal">
            <div class="search-modal__header">
                <div class="search-modal__input-wrapper">
                    <svg class="search-modal__icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                    </svg>
                    <input type="text" 
                           class="search-modal__input" 
                           placeholder="Buscar pedidos, clientes, órdenes..."
                           autofocus>
                </div>
            </div>
            <div class="search-modal__body">
                <div class="search-results"></div>
            </div>
        </div>
    `;

    const modal = this.showModal(modalContent, {
        title: false,
        closeButton: true
    });

    const searchInput = modal.querySelector('.search-modal__input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            DataLab.SearchModal.search(e.target.value);
        });
    }
};

// Inicializar el módulo de búsqueda
document.addEventListener('DOMContentLoaded', () => {
    DataLab.SearchModal.init();
});