document.addEventListener('DOMContentLoaded', () => {

    const productoInfo = {
        nombre: "Hamburguesa Especial",
        precioBase: 18000,
        imagen: "../static/images/hamburguesa.png"
    };

    const precioUnitarioTxt = document.getElementById('precio-unitario');
    const totalFinalTxt = document.getElementById('total-final');
    const cantTotalSpan = document.querySelector('.cantidad-total');
    const itemsAdicionales = document.querySelectorAll('.adicion-item');

    let cantidadProductos = 1;
    const VALOR_ADICIONAL = 3000;

    function actualizarPrecio() {
        let precioPorUnidad = productoInfo.precioBase;

        itemsAdicionales.forEach(item => {
            const cant = parseInt(item.querySelector('.cantidad').textContent);
            precioPorUnidad += cant * VALOR_ADICIONAL;

            if (cant > 0) {
                item.classList.add('seleccionado');
                
            } else {
                item.classList.remove('seleccionado');
            }
            item.style.backgroundColor = cant > 0 ? "#fff3cd" : "transparent";
                item.style.borderRadius = "8px";
        });

        const granTotal = precioPorUnidad * cantidadProductos;
        

        precioUnitarioTxt.textContent = `$${productoInfo.precioBase.toLocaleString()}`;
        totalFinalTxt.textContent = `$${granTotal.toLocaleString()}`;
        cantTotalSpan.textContent = cantidadProductos;
    }

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

    document.querySelector('.añadir').addEventListener('click', () => {
        let adicionalesElegidos = [];
        itemsAdicionales.forEach(item => {
            const c = item.querySelector('.cantidad').textContent;
            if (c > 0) adicionalesElegidos.push(`${item.querySelector('label').innerText} (x${c})`);
        });

        const resumen = `Producto: ${productoInfo.nombre}\nCantidad: ${cantidadProductos}\nAdicionales: ${adicionalesElegidos.join(', ') || 'Ninguno'}\nTotal: ${totalFinalTxt.textContent}`;
        
        alert("¡Pedido agregado!\n\n" + resumen);
    });

    actualizarPrecio();
});