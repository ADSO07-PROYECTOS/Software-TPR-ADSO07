document.addEventListener('DOMContentLoaded', () => {
    // 1. Datos del producto (Esto podría venir de una base de datos)
    // Por ahora, lo pondremos manual para probar
    const productoInfo = {
        nombre: "Hamburguesa Especial",
        precioBase: 18000,
        imagen: "../static/images/hamburguesa.png"
    };

    // 2. Elementos
    const precioUnitarioTxt = document.getElementById('precio-unitario');
    const totalFinalTxt = document.getElementById('total-final');
    const cantTotalSpan = document.querySelector('.cantidad-total');
    const itemsAdicionales = document.querySelectorAll('.adicion-item');

    let cantidadProductos = 1;
    const VALOR_ADICIONAL = 3000;

    // 3. Función de Cálculo
    function actualizarPrecio() {
        let precioPorUnidad = productoInfo.precioBase;

        // Sumar adicionales
        itemsAdicionales.forEach(item => {
            const cant = parseInt(item.querySelector('.cantidad').textContent);
            precioPorUnidad += cant * VALOR_ADICIONAL;

            // Cambio de color visual
            if (cant > 0) {
                item.classList.add('seleccionado');
                
            } else {
                item.classList.remove('seleccionado');
            }
            item.style.backgroundColor = cant > 0 ? "#fff3cd" : "transparent";
                item.style.borderRadius = "8px";
        });

        const granTotal = precioPorUnidad * cantidadProductos;
        
        // Mostrar en pantalla
        precioUnitarioTxt.textContent = `$${productoInfo.precioBase.toLocaleString()}`;
        totalFinalTxt.textContent = `$${granTotal.toLocaleString()}`;
        cantTotalSpan.textContent = cantidadProductos;
    }

    // 4. Eventos de los botones de adicionales
    itemsAdicionales.forEach(item => {
        item.querySelector('.btn-mas').addEventListener('click', () => {
            const span = item.querySelector('.cantidad');
            span.textContent = parseInt(span.textContent) + 1;
            
            actualizarPrecio();

            
        });

        item.querySelector('.btn-menos').addEventListener('click', () => {
            const span = item.querySelector('.cantidad');
            let v = parseInt(span.textContent);
            if (v > 0) {
                span.textContent = v - 1;
                actualizarPrecio();
            }
        });
    });

    // 5. Cantidad de productos (Footer)
    document.querySelector('.cont_btn-mas').addEventListener('click', () => {
        cantidadProductos++;
        actualizarPrecio();
    });

    document.querySelector('.cont_btn-menos').addEventListener('click', () => {
        if (cantidadProductos > 1) {
            cantidadProductos--;
            actualizarPrecio();
        }
    });

    // 6. Botón Añadir (Mensaje final)
    document.querySelector('.añadir').addEventListener('click', () => {
        let adicionalesElegidos = [];
        itemsAdicionales.forEach(item => {
            const c = item.querySelector('.cantidad').textContent;
            if (c > 0) adicionalesElegidos.push(`${item.querySelector('label').innerText} (x${c})`);
        });

        const resumen = `Producto: ${productoInfo.nombre}\nCantidad: ${cantidadProductos}\nAdicionales: ${adicionalesElegidos.join(', ') || 'Ninguno'}\nTotal: ${totalFinalTxt.textContent}`;
        
        alert("¡Pedido agregado!\n\n" + resumen);
    });

    // Iniciar
    actualizarPrecio();
});