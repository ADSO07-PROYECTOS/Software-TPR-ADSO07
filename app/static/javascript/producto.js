document.addEventListener('DOMContentLoaded', () => {
    // === 1. SELECCIÓN DE ELEMENTOS ===
    const selectTamano = document.getElementById('select-tamano');
    const displayPrecioBase = document.querySelector('.precio-btn');
    const displayPrecioFinal = document.querySelector('.precio-fn');
    const displayCantidadTotal = document.querySelector('.cantidad-total');
    
    // Elementos dinámicos
    const itemsAdicionales = document.querySelectorAll('.adicion-item');
    const checkboxesSabores = document.querySelectorAll('.lista-pizzas .check');
    
    // Botones globales
    const btnMasTotal = document.querySelector('.cont_btn-mas');
    const btnMenosTotal = document.querySelector('.cont_btn-menos');
    const botonAnadir = document.querySelector('.añadir');

    let cantidadDePizzas = 1;

    // === 2. FUNCIÓN DE VALIDACIÓN (Lee límites de la BD) ===
    function validarCombinaciones(event) {
        // Obtenemos el límite desde el atributo data-limite que pusimos con Jinja2
        const opcion = selectTamano.options[selectTamano.selectedIndex];
        const limite = parseInt(opcion.getAttribute('data-limite'));
        const nombreTamano = opcion.value;

        const seleccionados = document.querySelectorAll('.lista-pizzas .check:checked');
        const cantSeleccionada = seleccionados.length;

        // Validar exceso
        if (cantSeleccionada > limite) {
            // Solo alertamos si fue una acción directa del usuario (clic en checkbox)
            if (event && event.target && event.target.type === 'checkbox') {
                alert(`El tamaño ${nombreTamano} solo permite combinar ${limite} sabores.`);
                event.target.checked = false; 
            }
            return false;
        }

        // Bloqueo visual (Deshabilitar los no marcados)
        checkboxesSabores.forEach(check => {
            if (!check.checked) {
                check.disabled = (cantSeleccionada >= limite);
            } else {
                check.disabled = false;
            }
        });
        return true;
    }

    // === 3. FUNCIÓN DE CÁLCULO TOTAL ===
    function calcularTotal(event) {
        validarCombinaciones(event);

        // A. Precio Base (Desde BD -> HTML data-precio)
        const opcion = selectTamano.options[selectTamano.selectedIndex];
        let precioUnidad = parseFloat(opcion.getAttribute('data-precio'));

        if (displayPrecioBase) {
            displayPrecioBase.textContent = `$ ${precioUnidad.toLocaleString()}`;
        }

        // B. Sumar Adicionales (Precio dinámico desde data-precio)
        itemsAdicionales.forEach(item => {
            const span = item.querySelector('.cantidad');
            const cant = parseInt(span.textContent || span.innerText);
            const precioIndividual = parseFloat(item.getAttribute('data-precio'));
            
            if (cant > 0) {
                precioUnidad += (cant * precioIndividual);
                item.style.backgroundColor = "#fff3cd"; // Feedback visual
                item.style.borderRadius = "8px";
            } else {
                item.style.backgroundColor = "transparent";
            }
        });

        // C. Sumar Sabores (Precio dinámico desde data-precio)
        const saboresMarcados = document.querySelectorAll('.lista-pizzas .check:checked');
        saboresMarcados.forEach(check => {
            const precioSabor = parseFloat(check.getAttribute('data-precio'));
            precioUnidad += precioSabor;
        });

        // D. Total Final
        const granTotal = precioUnidad * cantidadDePizzas;
        
        // E. Renderizar
        displayCantidadTotal.textContent = cantidadDePizzas;
        displayPrecioFinal.textContent = `$ ${granTotal.toLocaleString()}`;
    }

    // === 4. EVENTOS ===

    // -- Adicionales (Botones + / -) --
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

    // -- Cantidad Pizzas --
    btnMasTotal.addEventListener('click', () => { cantidadDePizzas++; calcularTotal(); });
    btnMenosTotal.addEventListener('click', () => { if(cantidadDePizzas > 1){ cantidadDePizzas--; calcularTotal();} });

    // -- Cambios en select o checkboxes --
    selectTamano.addEventListener('change', (e) => {
        // Reiniciar sabores al cambiar tamaño para evitar conflictos
        checkboxesSabores.forEach(c => {c.checked = false; c.disabled = false;});
        calcularTotal(e);
    });
    
    checkboxesSabores.forEach(check => {
        check.addEventListener('change', (e) => calcularTotal(e));
    });

    // === 5. BOTÓN AÑADIR (Guardar y Redirigir) ===
    botonAnadir.addEventListener('click', () => {
        const opcion = selectTamano.options[selectTamano.selectedIndex];
        
        // Recolectar datos
        const nombrePizza = document.querySelector('h2').innerText;
        const tamanoNombre = opcion.value;
        const precioTotalTexto = displayPrecioFinal.innerText;

        // Lista Adicionales
        let listaAdicionales = [];
        itemsAdicionales.forEach(item => {
            const cant = parseInt(item.querySelector('.cantidad').innerText);
            if (cant > 0) {
                const nombre = item.querySelector('label').innerText;
                listaAdicionales.push(`${nombre} (x${cant})`);
            }
        });

        // Lista Sabores
        let listaSabores = [];
        document.querySelectorAll('.lista-pizzas .check:checked').forEach(check => {
            const nombre = check.parentElement.querySelector('label').innerText;
            listaSabores.push(nombre);
        });

        // Crear Objeto
        const pedido = {
            producto: nombrePizza,
            tamano: tamanoNombre,
            cantidad: cantidadDePizzas,
            adicionales: listaAdicionales,
            sabores: listaSabores,
            precio: precioTotalTexto
        };

        // Guardar y Redirigir
        localStorage.setItem('pedido_cliente', JSON.stringify(pedido));
        
        // CAMBIA ESTO por tu ruta real de resumen si es diferente
        window.location.href = "/resumen_pedido"; 
    });

    // Inicializar
    calcularTotal();
});