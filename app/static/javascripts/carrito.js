document.addEventListener('DOMContentLoaded', () => {
    const listaProductos = document.querySelector('.padre_ppal');
    const displayTotalTexto = document.querySelector('.total_valor'); 
    const botonPagar = document.querySelector('.total_btn'); 

    const actualizarTotales = () => {
        let totalGeneral = 0;
        const productos = document.querySelectorAll('.producto_detalles');

        productos.forEach(card => {
            const precioTexto = card.querySelector('.precio').innerText;
            const precioNumerico = parseInt(precioTexto.replace(/[^0-9]/g, ''));
            
            const cantidad = parseInt(card.querySelector('.seleccionar_cantidad span').innerText);
            
            totalGeneral += precioNumerico * cantidad;
        });

        const totalFormateado = totalGeneral.toLocaleString('es-CO');

        displayTotalTexto.innerHTML = `TOTAL: $ ${totalFormateado}`;
        botonPagar.innerText = `IR A PAGAR $ ${totalFormateado}`;
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
        else if (e.target.classList.contains('accion')) {
            card.remove();
        }

        actualizarTotales();
    });

    botonPagar.addEventListener('click', () => {
        const productosFinales = [];
        const cards = document.querySelectorAll('.producto_detalles');

        if (cards.length === 0) {
            alert("Tu carrito está vacío.");
            return;
        }

        cards.forEach(card => {
            productosFinales.push({
                nombre: card.querySelector('.ttlo_producto').innerText,
                precio: card.querySelector('.precio').innerText,
                cantidad: card.querySelector('.seleccionar_cantidad span').innerText
            });
        });

        localStorage.setItem('resumenCompra', JSON.stringify(productosFinales));
        
        window.location.href = "pago.html"; 
    });

    actualizarTotales();
});