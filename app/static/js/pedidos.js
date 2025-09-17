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
    
    // Mostrar el formulario por defecto
    if (formContainer) {
        toggleForm(true);
    }
});
