document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const btnNuevoPedido = document.getElementById('btn-nuevo-pedido');
    const btnEditarPedido = document.getElementById('btn-editar-pedido');
    const btnEliminarPedido = document.getElementById('btn-eliminar-pedido');
    const btnExportarPedido = document.getElementById('btn-exportar-pedido');
    const btnImprimirPedido = document.getElementById('btn-imprimir-pedido');
    const btnAyuda = document.getElementById('btn-ayuda');
    const searchInput = document.getElementById('search-pedido');
    const formPedido = document.getElementById('pedido-form');
    const formNuevoPedido = document.getElementById('form-nuevo-pedido');

    // State
    let pedidos = [];
    let selectedPedidoId = null;

    // Initialize
    initEventListeners();
    loadClientes();
    loadPedidos();

    function initEventListeners() {
        // Toolbar buttons
        btnNuevoPedido.addEventListener('click', showNuevoPedidoForm);
        btnEditarPedido.addEventListener('click', editarPedido);
        btnEliminarPedido.addEventListener('click', confirmarEliminarPedido);
        btnExportarPedido.addEventListener('click', exportarAPDF);
        btnImprimirPedido.addEventListener('click', imprimirPedido);
        btnAyuda.addEventListener('click', mostrarAyuda);

        // Search
        searchInput.addEventListener('input', (e) => {
            buscarPedidos(e.target.value);
        });

        // Form submission
        if (formPedido) {
            formPedido.addEventListener('submit', guardarPedido);
        }
    }

    // CRUD Operations
    async function loadPedidos() {
        try {
            // TODO: Replace with actual API call
            // const response = await fetch('/api/pedidos');
            // pedidos = await response.json();
            
            // Mock data for demonstration
            pedidos = [
                { id: 1, numero: 'PED-001', cliente: 'Cliente 1', fecha: '2023-11-01', estado: 'Pendiente', total: 1000 },
                { id: 2, numero: 'PED-002', cliente: 'Cliente 2', fecha: '2023-11-02', estado: 'En proceso', total: 1500 },
                { id: 3, numero: 'PED-003', cliente: 'Cliente 3', fecha: '2023-11-03', estado: 'Completado', total: 2000 },
            ];
            
            renderPedidos(pedidos);
        } catch (error) {
            console.error('Error al cargar los pedidos:', error);
            mostrarNotificacion('Error al cargar los pedidos', 'error');
        }
    }

    async function loadClientes() {
        try {
            // TODO: Replace with actual API call
            // const response = await fetch('/api/clientes');
            // const clientes = await response.json();
            
            // Mock data for demonstration
            const clientes = [
                { id: 1, nombre: 'Cliente 1' },
                { id: 2, nombre: 'Cliente 2' },
                { id: 3, nombre: 'Cliente 3' },
            ];
            
            const selectCliente = document.getElementById('cliente_id');
            if (selectCliente) {
                selectCliente.innerHTML = '<option value="" selected disabled>Seleccione un cliente...</option>';
                clientes.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id;
                    option.textContent = cliente.nombre;
                    selectCliente.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar los clientes:', error);
        }
    }

    function renderPedidos(pedidos) {
        const tbody = document.querySelector('#tabla-pedidos tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (pedidos.length === 0) {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td colspan="6" class="text-center py-4 text-gray-500">
                    No se encontraron pedidos
                </td>
            `;
            tbody.appendChild(tr);
            return;
        }
        
        pedidos.forEach(pedido => {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-gray-50 cursor-pointer';
            tr.dataset.id = pedido.id;
            
            tr.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-full bg-${getEstadoColor(pedido.estado)}-100">
                            <i class="fas ${getEstadoIcono(pedido.estado)} text-${getEstadoColor(pedido.estado)}-600"></i>
                        </div>
                        <div class="ml-4">
                            <div class="text-sm font-medium text-gray-900">${pedido.numero}</div>
                            <div class="text-sm text-gray-500">${pedido.cliente}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-${getEstadoColor(pedido.estado)}-100 text-${getEstadoColor(pedido.estado)}-800">
                        ${pedido.estado}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${formatFecha(pedido.fecha)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button class="text-indigo-600 hover:text-indigo-900 mr-4" data-action="edit" data-id="${pedido.id}">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="text-red-600 hover:text-red-900" data-action="delete" data-id="${pedido.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            
            tr.addEventListener('click', (e) => {
                if (!e.target.closest('button')) {
                    verDetallePedido(pedido.id);
                }
            });
            
            tbody.appendChild(tr);
        });
        
        // Add event listeners to action buttons
        document.querySelectorAll('[data-action="edit"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                editarPedido(parseInt(e.currentTarget.dataset.id));
            });
        });
        
        document.querySelectorAll('[data-action="delete"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                confirmarEliminarPedido(parseInt(e.currentTarget.dataset.id));
            });
        });
    }

    function getEstadoColor(estado) {
        const estados = {
            'Pendiente': 'yellow',
            'En proceso': 'blue',
            'Completado': 'green',
            'Cancelado': 'red'
        };
        return estados[estado] || 'gray';
    }
    
    function getEstadoIcono(estado) {
        const iconos = {
            'Pendiente': 'clock',
            'En proceso': 'spinner',
            'Completado': 'check-circle',
            'Cancelado': 'times-circle'
        };
        return `fa-${iconos[estado] || 'question-circle'}`;
    }
    
    function formatFecha(fecha) {
        return new Date(fecha).toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    // UI Functions
    function showNuevoPedidoForm() {
        formNuevoPedido.classList.remove('hidden');
        formPedido.reset();
        selectedPedidoId = null;
        
        // Scroll to form
        formNuevoPedido.scrollIntoView({ behavior: 'smooth' });
    }
    
    function verDetallePedido(id) {
        // TODO: Implementar vista de detalle
        console.log('Ver detalle del pedido:', id);
    }
    
    async function editarPedido(id) {
        // If id is not provided, use the selectedPedidoId
        const pedidoId = id || selectedPedidoId;
        if (!pedidoId) return;
        
        try {
            // TODO: Replace with actual API call
            // const response = await fetch(`/api/pedidos/${pedidoId}`);
            // const pedido = await response.json();
            
            // Mock data for demonstration
            const pedido = pedidos.find(p => p.id === pedidoId);
            
            if (pedido) {
                // Fill the form with pedido data
                document.getElementById('numero_pedido').value = pedido.numero || '';
                document.getElementById('cliente_id').value = pedido.cliente_id || '';
                // Fill other fields...
                
                // Show the form
                formNuevoPedido.classList.remove('hidden');
                selectedPedidoId = pedidoId;
                
                // Scroll to form
                formNuevoPedido.scrollIntoView({ behavior: 'smooth' });
            }
        } catch (error) {
            console.error('Error al cargar el pedido:', error);
            mostrarNotificacion('Error al cargar el pedido', 'error');
        }
    }
    
    async function guardarPedido(e) {
        e.preventDefault();
        
        const formData = new FormData(formPedido);
        const data = Object.fromEntries(formData.entries());
        
        try {
            let response;
            
            if (selectedPedidoId) {
                // Update existing pedido
                // response = await fetch(`/api/pedidos/${selectedPedidoId}`, {
                //     method: 'PUT',
                //     headers: { 'Content-Type': 'application/json' },
                //     body: JSON.stringify(data)
                // });
                mostrarNotificacion('Pedido actualizado correctamente', 'success');
            } else {
                // Create new pedido
                // response = await fetch('/api/pedidos', {
                //     method: 'POST',
                //     headers: { 'Content-Type': 'application/json' },
                //     body: JSON.stringify(data)
                // });
                mostrarNotificacion('Pedido creado correctamente', 'success');
            }
            
            // Refresh the pedidos list
            loadPedidos();
            
            // Hide the form
            formNuevoPedido.classList.add('hidden');
            
        } catch (error) {
            console.error('Error al guardar el pedido:', error);
            mostrarNotificacion('Error al guardar el pedido', 'error');
        }
    }
    
    function confirmarEliminarPedido(id) {
        const pedidoId = id || selectedPedidoId;
        if (!pedidoId) return;
        
        // TODO: Show a confirmation dialog
        if (confirm('¿Está seguro de eliminar este pedido?')) {
            eliminarPedido(pedidoId);
        }
    }
    
    async function eliminarPedido(id) {
        try {
            // TODO: Replace with actual API call
            // await fetch(`/api/pedidos/${id}`, { method: 'DELETE' });
            
            // Remove from local state
            pedidos = pedidos.filter(p => p.id !== id);
            renderPedidos(pedidos);
            
            mostrarNotificacion('Pedido eliminado correctamente', 'success');
            
            // Disable edit/delete buttons if no pedido is selected
            btnEditarPedido.disabled = true;
            btnEliminarPedido.disabled = true;
            
        } catch (error) {
            console.error('Error al eliminar el pedido:', error);
            mostrarNotificacion('Error al eliminar el pedido', 'error');
        }
    }
    
    function buscarPedidos(termino) {
        if (!termino.trim()) {
            renderPedidos(pedidos);
            return;
        }
        
        const terminoBusqueda = termino.toLowerCase();
        const resultados = pedidos.filter(pedido => 
            pedido.numero.toLowerCase().includes(terminoBusqueda) ||
            pedido.cliente.toLowerCase().includes(terminoBusqueda) ||
            pedido.estado.toLowerCase().includes(terminoBusqueda)
        );
        
        renderPedidos(resultados);
    }
    
    function exportarAPDF() {
        // TODO: Implement PDF export
        console.log('Exportar a PDF');
        mostrarNotificacion('Exportando a PDF...', 'info');
    }
    
    function imprimirPedido() {
        // TODO: Implement print functionality
        console.log('Imprimir pedido');
        window.print();
    }
    
    function mostrarAyuda() {
        // TODO: Show help modal or tooltip
        console.log('Mostrar ayuda');
        mostrarNotificacion('Sección de ayuda', 'info');
    }
    
    function mostrarNotificacion(mensaje, tipo = 'info') {
        // TODO: Implement a proper notification system
        alert(`${tipo.toUpperCase()}: ${mensaje}`);
    }
    
    // Initialize any plugins or additional functionality
    function initPlugins() {
        // Initialize tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});
