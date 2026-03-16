document.addEventListener('DOMContentLoaded', () => {

    const selectTamano = document.getElementById('select-tamano');
    const displayPrecioBase = document.querySelector('.precio-btn');
    const displayPrecioFinal = document.querySelector('.precio-fn');
    const displayCantidadTotal = document.querySelector('.cantidad-total');
    

    const itemsAdicionales = document.querySelectorAll('.adicion-item');
    const checkboxesSabores = document.querySelectorAll('.lista-pizzas .check');
    

    const btnMasTotal = document.querySelector('.cont_btn-mas');
    const btnMenosTotal = document.querySelector('.cont_btn-menos');
    const botonAnadir = document.querySelector('.añadir');

    let cantidadDePizzas = 1;

    const seccionCombinar = document.querySelector('.combinar');

    function validarCombinaciones(event) {

        const opcion = selectTamano.options[selectTamano.selectedIndex];
        if (!opcion) return true;
        const limite = parseInt(opcion.getAttribute('data-limite'));
        const nombreTamano = opcion.value;

        const seleccionados = document.querySelectorAll('.lista-pizzas .check:checked');
        const cantSeleccionada = seleccionados.length;

        if (cantSeleccionada > limite) {

            if (event && event.target && event.target.type === 'checkbox') {
                alert(`El tamaño ${nombreTamano} solo permite combinar ${limite} sabores.`);
                event.target.checked = false; 
            }
            return false;
        }

        checkboxesSabores.forEach(check => {
            if (!check.checked) {
                check.disabled = (cantSeleccionada >= limite);
            } else {
                check.disabled = false;
            }
        });
        return true;
    }

    function calcularTotal(event) {
        let precioUnidad;

        if (selectTamano) {
            validarCombinaciones(event);
            const opcion = selectTamano.options[selectTamano.selectedIndex];
            precioUnidad = parseFloat(opcion.getAttribute('data-precio'));
            if (displayPrecioBase) {
                displayPrecioBase.textContent = `$ ${precioUnidad.toLocaleString()}`;
            }
        } else {

            const platoSpan = document.getElementById('plato-id');
            precioUnidad = parseFloat(platoSpan.getAttribute('data-precio')) || 0;
        }

        itemsAdicionales.forEach(item => {
            const span = item.querySelector('.cantidad');
            const cant = parseInt(span.textContent || span.innerText);
            const precioIndividual = parseFloat(item.getAttribute('data-precio'));
            
            if (cant > 0) {
                precioUnidad += (cant * precioIndividual);
                item.style.backgroundColor = "#fff3cd";
                item.style.borderRadius = "8px";
            } else {
                item.style.backgroundColor = "transparent";
            }
        });

        if (selectTamano) {
            const saboresMarcados = document.querySelectorAll('.lista-pizzas .check:checked');
            saboresMarcados.forEach(check => {
                const precioSabor = parseFloat(check.getAttribute('data-precio'));
                precioUnidad += precioSabor;
            });
        }

        const granTotal = precioUnidad * cantidadDePizzas;
        

        displayCantidadTotal.textContent = cantidadDePizzas;
        displayPrecioFinal.textContent = `$ ${granTotal.toLocaleString()}`;
        displayPrecioFinal.dataset.precioUnitario = precioUnidad;
    }

    itemsAdicionales.forEach(item => {
        item.querySelector('.btn-mas').addEventListener('click', () => {
            const span = item.querySelector('.cantidad');
            span.textContent = parseInt(span.textContent) + 1;
            calcularTotal();
        });

        item.querySelector('.btn-menos').addEventListener('click', () => {
            const span = item.querySelector('.cantidad');
            let valor = parseInt(span.textContent);
            if (valor > 0) {
                span.textContent = valor - 1;
                calcularTotal();
            }
        });
    });

    btnMasTotal.addEventListener('click', () => { cantidadDePizzas++; calcularTotal(); });
    btnMenosTotal.addEventListener('click', () => { if(cantidadDePizzas > 1){ cantidadDePizzas--; calcularTotal();} });

    if (selectTamano) {
        selectTamano.addEventListener('change', (e) => {

            checkboxesSabores.forEach(c => {c.checked = false; c.disabled = false;});
            gestionarVisibilidadCombinar();
            calcularTotal(e);
        });
    }
    
    checkboxesSabores.forEach(check => {
        check.addEventListener('change', (e) => calcularTotal(e));
    });

    botonAnadir.addEventListener('click', () => {
        let tamanoNombre = '';
        let precioUnitario;

        if (selectTamano) {
            const opcion = selectTamano.options[selectTamano.selectedIndex];
            tamanoNombre = opcion.value;
            precioUnitario = parseFloat(displayPrecioFinal.dataset.precioUnitario || opcion.getAttribute('data-precio'));
        } else {
            const platoSpan = document.getElementById('plato-id');
            precioUnitario = parseFloat(displayPrecioFinal.dataset.precioUnitario || platoSpan.getAttribute('data-precio'));
        }
        

        const nombrePizza = document.querySelector('h2').innerText;

        let listaAdicionales = [];
        itemsAdicionales.forEach(item => {
            const cant = parseInt(item.querySelector('.cantidad').innerText);
            if (cant > 0) {
                const nombreEl = item.querySelector('label') || item.querySelector('.adicion-nombre span');
                const nombre = nombreEl ? nombreEl.innerText : '';
                listaAdicionales.push(`${nombre} (x${cant})`);
            }
        });

        let listaSabores = [];
        document.querySelectorAll('.lista-pizzas .check:checked').forEach(check => {
            const nombre = check.parentElement.querySelector('label').innerText;
            listaSabores.push(nombre);
        });

        const platoId = parseInt(document.getElementById('plato-id').getAttribute('data-id')) || null;
        const pedido = {
            id: platoId,
            producto: nombrePizza,
            tamano: tamanoNombre,
            cantidad: cantidadDePizzas,
            adicionales: listaAdicionales,
            sabores: listaSabores,
            precio_unitario: precioUnitario,
            precio: precioUnitario * cantidadDePizzas
        };

        const carritoActual = JSON.parse(localStorage.getItem('carrito') || '[]');
        carritoActual.push(pedido);
        localStorage.setItem('carrito', JSON.stringify(carritoActual));
        
        window.location.href = "/carrito"; 
    });

    function gestionarVisibilidadCombinar() {
        if (!seccionCombinar || !selectTamano) return;
        const opcion = selectTamano.options[selectTamano.selectedIndex];
        if (!opcion) {
            seccionCombinar.style.display = 'none';
            return;
        }
        const limite = parseInt(opcion.getAttribute('data-limite'));
        if (limite > 1) {
            seccionCombinar.style.display = 'block';
        } else {
            seccionCombinar.style.display = 'none';

            checkboxesSabores.forEach(c => { c.checked = false; });
        }
    }

    gestionarVisibilidadCombinar();
    calcularTotal();
});