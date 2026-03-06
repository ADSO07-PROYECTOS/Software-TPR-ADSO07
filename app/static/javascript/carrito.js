document.addEventListener('DOMContentLoaded', () => {
    // Limpiar items viejos sin campo 'id' (datos anteriores a la versión actual)
    const carritoRaw = JSON.parse(localStorage.getItem('carrito') || '[]');
    const carritoLimpio = carritoRaw.filter(item => item.id != null);
    if (carritoLimpio.length !== carritoRaw.length) {
        localStorage.setItem('carrito', JSON.stringify(carritoLimpio));
    }

    const listaProductos = document.querySelector('.padre_ppal');
    const displayTotalTexto = document.querySelector('.total_valor'); 
    const botonPagar = document.querySelector('.total_btn'); 

    // === Renderizar items desde localStorage ===
    const cargarCarrito = () => {
        const items = JSON.parse(localStorage.getItem('carrito') || '[]');

        // Limpiar tarjetas previas
        document.querySelectorAll('.producto_detalles').forEach(el => el.remove());

        const metodoPago = listaProductos.querySelector('.metodo-pago');

        if (items.length === 0) {
            const vacio = document.createElement('p');
            vacio.classList.add('carrito-vacio');
            vacio.textContent = 'Tu carrito está vacío.';
            listaProductos.insertBefore(vacio, metodoPago);
        }

        items.forEach((item, index) => {
            document.querySelector('.carrito-vacio')?.remove();
            const div = document.createElement('div');
            div.classList.add('producto_detalles');
            div.setAttribute('data-index', index);
            div.setAttribute('data-item', JSON.stringify(item));

            let descripcionExtra = '';
            if (item.tamano) {
                descripcionExtra += `<span class="descripcion-extra">${item.tamano}</span>`;
            }
            if (item.adicionales && item.adicionales.length > 0) {
                descripcionExtra += `<span class="descripcion-extra">${item.adicionales.join(', ')}</span>`;
            }
            if (item.sabores && item.sabores.length > 0) {
                descripcionExtra += `<span class="descripcion-extra">Sabores: ${item.sabores.join(', ')}</span>`;
            }

            div.innerHTML = `
                <div class="precio_seccion">
                    <span class="ttlo_producto">${item.producto}</span>
                    ${descripcionExtra}
                    <span class="precio">$ ${(item.precio || 0).toLocaleString('es-CO')}</span>
                </div>
                <div class="controles">
                    <div class="seleccionar_cantidad">
                        <button>-</button>
                        <span>${item.cantidad}</span>
                        <button>+</button>
                    </div>
                    <div class="acciones">
                        <button class="accion">Eliminar</button>
                    </div>
                </div>
            `;
            listaProductos.insertBefore(div, metodoPago);
        });

        actualizarTotales();
    };

    const actualizarTotales = () => {
        let totalGeneral = 0;
        const productos = document.querySelectorAll('.producto_detalles');

        productos.forEach(card => {
            const precioTexto = card.querySelector('.precio').innerText;
            const precioNumerico = parseInt(precioTexto.replace(/[^0-9]/g, '')) || 0;
            totalGeneral += precioNumerico; // El precio ya es el subtotal del ítem
        });

        const totalFormateado = totalGeneral.toLocaleString('es-CO');
        displayTotalTexto.innerHTML = `TOTAL: $ ${totalFormateado}`;
        botonPagar.innerText = `IR A PAGAR $ ${totalFormateado}`;

        // Sincronizar cambios de cantidad/eliminación al localStorage
        sincronizarLocalStorage();
    };

    const sincronizarLocalStorage = () => {
        const cards = document.querySelectorAll('.producto_detalles');
        const carritoActualizado = [];
        cards.forEach(card => {
            const itemOriginal = JSON.parse(card.getAttribute('data-item') || '{}');
            const nuevaCantidad = parseInt(card.querySelector('.seleccionar_cantidad span').innerText);
            const precioUnitario = itemOriginal.precio_unitario || 0;
            carritoActualizado.push({
                ...itemOriginal,
                cantidad: nuevaCantidad,
                precio: precioUnitario * nuevaCantidad
            });
            // Actualizar data-item con la cantidad nueva
            card.setAttribute('data-item', JSON.stringify({ ...itemOriginal, cantidad: nuevaCantidad, precio: precioUnitario * nuevaCantidad }));
        });
        localStorage.setItem('carrito', JSON.stringify(carritoActualizado));
    };

    listaProductos.addEventListener('click', (e) => {
        const card = e.target.closest('.producto_detalles');
        if (!card) return;

        const spanCantidad = card.querySelector('.seleccionar_cantidad span');
        let cantidadActual = parseInt(spanCantidad.innerText);

        if (e.target.innerText === '+') {
            spanCantidad.innerText = cantidadActual + 1;
        } 
        else if (e.target.innerText === '-') {
            if (cantidadActual > 1) {
                spanCantidad.innerText = cantidadActual - 1;
            }
        }

        // Actualizar precio mostrado del ítem según nueva cantidad
        if (e.target.innerText === '+' || e.target.innerText === '-') {
            const itemData = JSON.parse(card.getAttribute('data-item') || '{}');
            const precioUnitario = itemData.precio_unitario || 0;
            const nuevaCantidad = parseInt(spanCantidad.innerText);
            const spanPrecio = card.querySelector('.precio');
            spanPrecio.innerText = `$ ${(precioUnitario * nuevaCantidad).toLocaleString('es-CO')}`;
        } 
        else if (e.target.classList.contains('accion')) {
            card.remove();
            if (document.querySelectorAll('.producto_detalles').length === 0) {
                const metodoPago = listaProductos.querySelector('.metodo-pago');
                const vacio = document.createElement('p');
                vacio.classList.add('carrito-vacio');
                vacio.textContent = 'Tu carrito está vacío.';
                listaProductos.insertBefore(vacio, metodoPago);
            }
        }

        actualizarTotales();
    });

    // === Modal de selección de servicio ===
    const modal = document.getElementById('modal-servicio');

    botonPagar.addEventListener('click', () => {
        const cards = document.querySelectorAll('.producto_detalles');
        if (cards.length === 0) {
            alert('Tu carrito está vacío.');
            return;
        }
        modal.style.display = 'flex';
    });

    document.getElementById('btn-modal-cancelar').addEventListener('click', () => {
        modal.style.display = 'none';
    });

    const irAServicio = (tipo) => {
        // Copiar carrito al key que leen los microservicios
        const carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
        const carritoTpr = carrito.map(item => ({
            id: item.id,
            nombre: item.producto,
            cantidad: item.cantidad,
            precio: item.precio_unitario || item.precio,
            tamano: item.tamano || '',
            adicionales: item.adicionales || [],
            sabores: item.sabores || []
        }));
        localStorage.setItem('carrito_tpr', JSON.stringify(carritoTpr));
        localStorage.setItem('tipo_servicio', tipo);
        window.location.href = '/datos_cliente';
    };

    document.getElementById('btn-modal-reserva').addEventListener('click', () => irAServicio('reserva'));
    document.getElementById('btn-modal-domicilio').addEventListener('click', () => irAServicio('domicilio'));

    cargarCarrito();
});