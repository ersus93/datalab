/**
 * Funcionalidad para la gestión de pedidos
 */

document.addEventListener('DOMContentLoaded', function() {
    const formPedido = document.getElementById('pedido-form');
    const btnNuevoPedido = document.getElementById('btn-nuevo-pedido');
    const formContainer = document.getElementById('form-nuevo-pedido');
    const btnCancelar = document.getElementById('btn-cancelar');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('btn-text');
    const clienteSelect = document.getElementById('cliente_id');

    // Cargar clientes
    async function cargarClientes() {
        try {
            const response = await fetch('/pedidos/clientes');
            const data = await response.json();
            
            if (data.success) {
                clienteSelect.innerHTML = '<option value="" selected disabled>Seleccione un cliente...</option>';
                data.clientes.forEach(cliente => {
                    const option = document.createElement('option');
                    option.value = cliente.id;
                    option.textContent = `${cliente.nombre} (${cliente.identificacion || 'Sin identificación'})`;
                    clienteSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error al cargar clientes:', error);
            alert('Error al cargar la lista de clientes');
        }
    }

    // Función para cargar los últimos clientes agregados
    async function cargarUltimosClientes() {
        try {
            const response = await fetch('/pedidos/ultimos_clientes');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            const ultimosClientesList = document.getElementById('ultimos-clientes-list');
            ultimosClientesList.innerHTML = ''; // Limpiar el contenido actual

            if (data.length > 0) {
                data.forEach(cliente => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td><span class="client-name">${cliente.nombre}</span></td>
                        <td><span class="client-email">${cliente.email}</span></td>
                        <td>${cliente.telefono || 'N/A'}</td>
                        <td>${new Date(cliente.fecha_registro).toLocaleDateString()}</td>
                    `;
                    ultimosClientesList.appendChild(row);
                });
            } else {
                ultimosClientesList.innerHTML = `
                    <tr>
                        <td colspan="4" class="text-center">No hay clientes recientes.</td>
                    </tr>
                `;
            }
        } catch (error) {
            console.error('Error al cargar los últimos clientes:', error);
            const ultimosClientesList = document.getElementById('ultimos-clientes-list');
            ultimosClientesList.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-danger">Error al cargar clientes.</td>
                </tr>
            `;
        }
    }

    // Cargar clientes al iniciar la página
    cargarClientesDropdown();
    cargarUltimosClientes();

    // Manejar envío del formulario
    formPedido.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        if (!formPedido.checkValidity()) {
            e.stopPropagation();
            formPedido.classList.add('was-validated');
            return;
        }

        const formData = {
            numero_pedido: document.getElementById('numero_pedido').value,
            cliente_id: document.getElementById('cliente_id').value,
            descripcion: document.getElementById('descripcion').value
        };

        try {
            // Mostrar spinner
            spinner.classList.remove('d-none');
            btnText.textContent = 'Guardando...';
            
            const response = await fetch('/pedidos/nuevo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            const data = await response.json();

            if (data.success) {
                alert('Pedido creado exitosamente');
                formPedido.reset();
                formPedido.classList.remove('was-validated');
                // Aquí podrías redirigir a la página de detalle del pedido o actualizar la lista
                // window.location.href = `/pedidos/${data.pedido_id}`;
            } else {
                throw new Error(data.error || 'Error al crear el pedido');
            }
        } catch (error) {
            console.error('Error:', error);
            alert(`Error: ${error.message}`);
        } finally {
            spinner.classList.add('d-none');
            btnText.textContent = 'Guardar Pedido';
        }
    });

    // Mostrar/ocultar formulario
    function toggleForm(show = true) {
        if (show) {
            formContainer.style.display = 'block';
            window.scrollTo({
                top: formContainer.offsetTop - 20,
                behavior: 'smooth'
            });
        } else {
            formContainer.style.display = 'none';
        }
    }

    // Event listeners
    if (btnNuevoPedido) {
        btnNuevoPedido.addEventListener('click', () => toggleForm(true));
    }
    
    if (btnCancelar) {
        btnCancelar.addEventListener('click', () => toggleForm(false));
    }

    // Cargar clientes al iniciar
    if (clienteSelect) {
        cargarClientes();
    }
    
    // Cargar últimos clientes al iniciar
    cargarUltimosClientes();

    // Mostrar el formulario por defecto
    if (formContainer) {
        toggleForm(true);
    }
});
