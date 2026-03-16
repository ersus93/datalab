/**
 * Batch Operations JavaScript Module
 * Handles sample selection, filtering, and batch status updates
 * Issue #45 - Batch operations for sample status management
 */

(function() {
    'use strict';

    // Module state
    let dataTable = null;
    let selectedIds = new Set();
    let samplesData = [];

    // DOM Elements
    const elements = {
        table: document.getElementById('samples-table'),
        selectAll: document.getElementById('select-all'),
        selectAllHeader: document.getElementById('select-all-header'),
        selectedCount: document.getElementById('selected-count'),
        totalMuestras: document.getElementById('total-muestras'),
        filterStatus: document.getElementById('filter-status'),
        filterDesde: document.getElementById('filter-desde'),
        filterHasta: document.getElementById('filter-hasta'),
        filterCliente: document.getElementById('filter-cliente'),
        btnAplicarFiltros: document.getElementById('btn-aplicar-filtros'),
        btnLimpiarFiltros: document.getElementById('btn-limpiar-filtros'),
        batchAction: document.getElementById('batch-action'),
        batchReason: document.getElementById('batch-reason'),
        btnPreview: document.getElementById('btn-preview'),
        btnExecute: document.getElementById('btn-execute'),
        progressContainer: document.getElementById('progress-container'),
        progressBar: document.getElementById('progress-bar'),
        progressText: document.getElementById('progress-text'),
        progressStatus: document.getElementById('progress-status'),
        resultsContainer: document.getElementById('results-container'),
        resultsSuccess: document.getElementById('results-success'),
        resultsFailed: document.getElementById('results-failed'),
        resultsTotal: document.getElementById('results-total'),
        resultsErrors: document.getElementById('results-errors'),
        errorsList: document.getElementById('errors-list'),
        btnNewOperation: document.getElementById('btn-new-operation'),
        previewModal: document.getElementById('preview-modal'),
        btnCloseModal: document.getElementById('btn-close-modal'),
        btnCancelModal: document.getElementById('btn-cancel-modal'),
        btnConfirmModal: document.getElementById('btn-confirm-modal'),
        previewAction: document.getElementById('preview-action'),
        previewReason: document.getElementById('preview-reason'),
        previewCount: document.getElementById('preview-count'),
        previewTableBody: document.getElementById('preview-table-body')
    };

    // Status labels and classes
    const statusConfig = {
        'RECIBIDO': { label: 'Recibido', class: 'status-recibido' },
        'EN_PROCESO': { label: 'En Proceso', class: 'status-en-proceso' },
        'COMPLETADO': { label: 'Completado', class: 'status-completado' },
        'ENTREGADO': { label: 'Entregado', class: 'status-entregado' },
        'ANULADO': { label: 'Anulado', class: 'status-anulado' }
    };

    /**
     * Initialize the module
     */
    function init() {
        initDataTable();
        bindEvents();
        loadSamples();
    }

    /**
     * Initialize DataTable
     */
    function initDataTable() {
        dataTable = $(elements.table).DataTable({
            language: {
                url: '//cdn.datatables.net/plug-ins/1.13.7/i18n/es-ES.json'
            },
            columns: [
                {
                    data: null,
                    orderable: false,
                    className: 'dt-center',
                    render: function(data, type, row) {
                        return `<input type="checkbox" class="dt-checkbox row-checkbox" data-id="${row.id}" ${selectedIds.has(row.id) ? 'checked' : ''}>`;
                    }
                },
                { data: 'codigo', render: renderCodigo },
                { data: 'lote', defaultContent: '-' },
                { data: 'producto', defaultContent: '-' },
                { data: 'cliente', defaultContent: '-' },
                { data: 'status', render: renderStatus },
                { data: 'cantidad_recib' },
                { data: 'fech_entrada', render: renderDate }
            ],
            order: [[1, 'asc']],
            pageLength: 25,
            processing: true,
            deferRender: true,
            scrollX: true
        });

        // Handle checkbox clicks in table
        $(elements.table).on('change', '.row-checkbox', function() {
            const id = parseInt(this.dataset.id);
            if (this.checked) {
                selectedIds.add(id);
            } else {
                selectedIds.delete(id);
            }
            updateSelectionUI();
        });
    }

    /**
     * Render codigo with link
     */
    function renderCodigo(data, type, row) {
        return `<a href="/entradas/${row.id}" class="text-blue-600 hover:text-blue-800 font-medium" target="_blank">${data}</a>`;
    }

    /**
     * Render status badge
     */
    function renderStatus(data) {
        const config = statusConfig[data] || { label: data, class: '' };
        return `<span class="status-badge ${config.class}">${config.label}</span>`;
    }

    /**
     * Render date
     */
    function renderDate(data) {
        if (!data) return '-';
        const date = new Date(data);
        return date.toLocaleDateString('es-ES');
    }

    /**
     * Bind event handlers
     */
    function bindEvents() {
        // Filter buttons
        elements.btnAplicarFiltros.addEventListener('click', loadSamples);
        elements.btnLimpiarFiltros.addEventListener('click', clearFilters);

        // Select all checkboxes
        elements.selectAll.addEventListener('change', toggleSelectAll);
        elements.selectAllHeader.addEventListener('change', toggleSelectAll);

        // Batch action controls
        elements.batchAction.addEventListener('change', validateForm);
        elements.batchReason.addEventListener('input', validateForm);

        // Action buttons
        elements.btnPreview.addEventListener('click', showPreview);
        elements.btnExecute.addEventListener('click', () => showPreview());

        // Modal buttons
        elements.btnCloseModal.addEventListener('click', hideModal);
        elements.btnCancelModal.addEventListener('click', hideModal);
        elements.btnConfirmModal.addEventListener('click', executeBatch);

        // Results buttons
        elements.btnNewOperation.addEventListener('click', resetOperation);

        // Close modal on backdrop click
        elements.previewModal.addEventListener('click', function(e) {
            if (e.target === this) hideModal();
        });
    }

    /**
     * Load samples from API
     */
    async function loadSamples() {
        try {
            const filters = {
                status: elements.filterStatus.value,
                desde: elements.filterDesde.value,
                hasta: elements.filterHasta.value,
                cliente: elements.filterCliente.value
            };

            const params = new URLSearchParams();
            Object.entries(filters).forEach(([key, value]) => {
                if (value) params.append(key, value);
            });

            // Show loading state
            dataTable.processing(true);

            const response = await fetch(`/api/entradas?${params.toString()}`);
            if (!response.ok) throw new Error('Error al cargar muestras');

            samplesData = await response.json();

            // Clear and reload table
            dataTable.clear().rows.add(samplesData).draw();
            elements.totalMuestras.textContent = samplesData.length;

            // Restore selections
            updateRowCheckboxes();
            updateSelectionUI();

        } catch (error) {
            console.error('Error loading samples:', error);
            showNotification('Error al cargar las muestras', 'error');
        } finally {
            dataTable.processing(false);
        }
    }

    /**
     * Clear all filters
     */
    function clearFilters() {
        elements.filterStatus.value = '';
        elements.filterDesde.value = '';
        elements.filterHasta.value = '';
        elements.filterCliente.value = '';
        loadSamples();
    }

    /**
     * Toggle select all visible rows
     */
    function toggleSelectAll() {
        const isChecked = this.checked;
        const visibleRows = dataTable.rows({ page: 'current' }).data().toArray();

        visibleRows.forEach(row => {
            if (isChecked) {
                selectedIds.add(row.id);
            } else {
                selectedIds.delete(row.id);
            }
        });

        elements.selectAll.checked = isChecked;
        elements.selectAllHeader.checked = isChecked;

        updateRowCheckboxes();
        updateSelectionUI();
    }

    /**
     * Update checkbox states in table rows
     */
    function updateRowCheckboxes() {
        document.querySelectorAll('.row-checkbox').forEach(checkbox => {
            const id = parseInt(checkbox.dataset.id);
            checkbox.checked = selectedIds.has(id);
        });
    }

    /**
     * Update selection UI
     */
    function updateSelectionUI() {
        const count = selectedIds.size;
        elements.selectedCount.textContent = `(${count} seleccionadas)`;
        validateForm();
    }

    /**
     * Validate form and enable/disable buttons
     */
    function validateForm() {
        const hasSelection = selectedIds.size > 0;
        const hasAction = elements.batchAction.value !== '';
        const hasReason = elements.batchReason.value.trim().length > 0;

        const isValid = hasSelection && hasAction && hasReason;

        elements.btnPreview.disabled = !isValid;
        elements.btnExecute.disabled = !isValid;
    }

    /**
     * Show preview modal
     */
    function showPreview() {
        const action = elements.batchAction.value;
        const reason = elements.batchReason.value.trim();
        const selectedSamples = samplesData.filter(s => selectedIds.has(s.id));

        if (!action || !reason || selectedSamples.length === 0) {
            showNotification('Por favor complete todos los campos', 'warning');
            return;
        }

        const actionConfig = statusConfig[action];
        elements.previewAction.textContent = `Cambiar a: ${actionConfig.label}`;
        elements.previewReason.textContent = reason;
        elements.previewCount.textContent = `${selectedSamples.length} muestras`;

        // Build preview table
        elements.previewTableBody.innerHTML = selectedSamples.map(sample => {
            const currentConfig = statusConfig[sample.status] || { label: sample.status };
            return `
                <tr class="border-b">
                    <td class="px-4 py-2 font-medium">${sample.codigo}</td>
                    <td class="px-4 py-2"><span class="status-badge ${currentConfig.class}">${currentConfig.label}</span></td>
                    <td class="px-4 py-2"><span class="status-badge ${actionConfig.class}">${actionConfig.label}</span></td>
                </tr>
            `;
        }).join('');

        elements.previewModal.classList.remove('hidden');
    }

    /**
     * Hide preview modal
     */
    function hideModal() {
        elements.previewModal.classList.add('hidden');
    }

    /**
     * Execute batch operation
     */
    async function executeBatch() {
        hideModal();

        const payload = {
            ids: Array.from(selectedIds),
            status: elements.batchAction.value,
            razon: elements.batchReason.value.trim()
        };

        // Show progress
        elements.progressContainer.classList.add('active');
        updateProgress(0, 'Iniciando operación...');

        try {
            // Simulate progress updates
            const progressInterval = setInterval(() => {
                const current = parseInt(elements.progressBar.style.width) || 0;
                if (current < 90) {
                    updateProgress(current + Math.random() * 20, 'Procesando...');
                }
            }, 500);

            const response = await fetch('/api/status/entrada/batch-change', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify(payload)
            });

            clearInterval(progressInterval);

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || 'Error en la operación');
            }

            updateProgress(100, 'Completado');
            showResults(result);

        } catch (error) {
            console.error('Batch operation error:', error);
            updateProgress(0, 'Error');
            showResults({
                success: 0,
                failed: selectedIds.size,
                total: selectedIds.size,
                errors: [error.message]
            });
        }
    }

    /**
     * Update progress bar
     */
    function updateProgress(percentage, status) {
        const normalized = Math.min(100, Math.max(0, percentage));
        elements.progressBar.style.width = `${normalized}%`;
        elements.progressText.textContent = `${Math.round(normalized)}%`;
        elements.progressStatus.textContent = status;
    }

    /**
     * Show operation results
     */
    function showResults(result) {
        elements.progressContainer.classList.remove('active');
        elements.resultsContainer.classList.add('active');

        elements.resultsSuccess.textContent = result.success || 0;
        elements.resultsFailed.textContent = result.failed || 0;
        elements.resultsTotal.textContent = result.total || selectedIds.size;

        // Show errors if any
        if (result.errors && result.errors.length > 0) {
            elements.resultsErrors.classList.remove('hidden');
            elements.errorsList.innerHTML = result.errors.map(e => `<li>${e}</li>`).join('');
        } else {
            elements.resultsErrors.classList.add('hidden');
        }

        // Scroll to results
        elements.resultsContainer.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Reset for new operation
     */
    function resetOperation() {
        selectedIds.clear();
        elements.batchAction.value = '';
        elements.batchReason.value = '';
        elements.resultsContainer.classList.remove('active');
        updateSelectionUI();
        updateRowCheckboxes();
        loadSamples();
    }

    /**
     * Get CSRF token from meta tag or cookie
     */
    function getCsrfToken() {
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.content;

        // Try to get from cookie
        const match = document.cookie.match(/csrf_token=([^;]+)/);
        return match ? match[1] : '';
    }

    /**
     * Show notification (uses flash messages or custom notification)
     */
    function showNotification(message, type = 'info') {
        // Check if there's a global notification function
        if (typeof window.showFlashMessage === 'function') {
            window.showFlashMessage(message, type);
        } else {
            alert(message);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose module for testing/debugging
    window.BatchOperations = {
        selectedIds,
        samplesData,
        refresh: loadSamples
    };

})();
