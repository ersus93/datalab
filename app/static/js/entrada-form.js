/**
 * Manejo del formulario de entradas con validación avanzada
 */
class EntradaForm {
    constructor() {
        this.form = document.getElementById('entrada-form');
        if (this.form) {
            this.init();
        }
    }

    init() {
        this.setupValidation();
        this.setupCalculations();
        this.setupSelectors();
    }

    setupValidation() {
        // Validación de lote X-XXXX
        const loteInput = document.getElementById('lote');
        if (loteInput) {
            loteInput.addEventListener('blur', (e) => {
                this.validateLote(e.target);
            });
        }

        // Validación de fechas
        const fechFab = document.getElementById('fech_fab');
        const fechVenc = document.getElementById('fech_venc');

        if (fechFab && fechVenc) {
            const validateDates = () => {
                const errorEl = document.getElementById('fecha-error');
                if (fechFab.value && fechVenc.value) {
                    if (new Date(fechVenc.value) <= new Date(fechFab.value)) {
                        fechVenc.classList.add('border-red-500');
                        fechVenc.classList.remove('border-gray-300');
                        if (errorEl) errorEl.classList.remove('hidden');
                    } else {
                        fechVenc.classList.remove('border-red-500');
                        fechVenc.classList.add('border-gray-300');
                        if (errorEl) errorEl.classList.add('hidden');
                    }
                }
            };

            fechFab.addEventListener('change', validateDates);
            fechVenc.addEventListener('change', validateDates);
        }

        // Validación de cantidades
        const cantRecib = document.getElementById('cantidad_recib');
        if (cantRecib) {
            cantRecib.addEventListener('input', (e) => {
                const value = parseFloat(e.target.value);
                if (value <= 0) {
                    this.showError(e.target, 'La cantidad debe ser mayor a 0');
                } else {
                    this.clearError(e.target);
                }
            });
        }

        // Validación al enviar
        this.form.addEventListener('submit', (e) => {
            if (!this.validateForm()) {
                e.preventDefault();
                e.stopPropagation();
                this.showFormErrors();
            }
        });
    }

    setupCalculations() {
        // Cálculo de saldo
        const cantRecib = document.getElementById('cantidad_recib');
        const saldoDisplay = document.getElementById('saldo-display');

        if (cantRecib && saldoDisplay) {
            cantRecib.addEventListener('input', () => {
                const recib = parseFloat(cantRecib.value) || 0;
                saldoDisplay.value = recib.toFixed(2);
            });
        }

        // Actualizar unidad mostrada
        const unidadSelect = document.getElementById('unidad_medida_id');
        const unidadDisplay = document.getElementById('unidad-display');

        if (unidadSelect && unidadDisplay) {
            unidadSelect.addEventListener('change', () => {
                const selected = unidadSelect.options[unidadSelect.selectedIndex];
                const text = selected ? selected.text : '-';
                unidadDisplay.textContent = text.split(' - ')[0] || '-';
            });
        }
    }

    setupSelectors() {
        // Toggle pedido
        const linkPedido = document.getElementById('link-pedido');
        const pedidoRow = document.getElementById('pedido-row');

        if (linkPedido && pedidoRow) {
            linkPedido.addEventListener('change', () => {
                pedidoRow.style.display = linkPedido.checked ? 'block' : 'none';
            });
        }
    }

    validateForm() {
        let isValid = true;

        // Validar fábrica
        const fabricaSelect = document.getElementById('fabrica-select');
        if (fabricaSelect && !fabricaSelect.value) {
            isValid = false;
            document.getElementById('fabrica-error')?.classList.remove('hidden');
        }

        // Validar producto
        const productoSelect = document.getElementById('producto-select');
        if (productoSelect && !productoSelect.value) {
            isValid = false;
            document.getElementById('producto-error')?.classList.remove('hidden');
        }

        // Validar fechas
        const fechFab = document.getElementById('fech_fab');
        const fechVenc = document.getElementById('fech_venc');
        if (fechFab && fechVenc && fechFab.value && fechVenc.value) {
            if (new Date(fechVenc.value) <= new Date(fechFab.value)) {
                isValid = false;
            }
        }

        return isValid;
    }

    validateLote(input) {
        const value = input.value.trim();
        if (value && !/^[A-Z]-\d{4}$/.test(value)) {
            this.showError(input, 'Formato debe ser X-XXXX (ej: A-1234)');
            return false;
        } else {
            this.clearError(input);
            return true;
        }
    }

    showError(input, message) {
        input.classList.add('border-red-500');
        input.classList.remove('border-gray-300');

        let feedback = input.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('p');
            feedback.className = 'text-red-500 text-xs mt-1 invalid-feedback';
            input.parentElement.appendChild(feedback);
        }
        feedback.textContent = message;
    }

    clearError(input) {
        input.classList.remove('border-red-500');
        input.classList.add('border-gray-300');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.remove();
        }
    }

    showFormErrors() {
        // Scroll al primer error
        const firstError = this.form.querySelector('.border-red-500');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstError.focus();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new EntradaForm();
});
