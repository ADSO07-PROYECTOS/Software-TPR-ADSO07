document.addEventListener('DOMContentLoaded', () => {
    // === 1. SELECCIÓN DE ELEMENTOS DEL DOM ===
    const selectTamano = document.querySelector('.tamano-pizza');
    const displayPrecioBase = document.querySelector('.precio-btn');
    const displayPrecioFinal = document.querySelector('.precio-fn');
    const itemsAdicionales = document.querySelectorAll('.adicion-item');
    const botonAnadir = document.querySelector('.añadir'); // Asegúrate que tu botón tenga esta clase
    const btnMasTotal = document.querySelector('.cont_btn-mas');
    const btnMenosTotal = document.querySelector('.cont_btn-menos');
    const displayCantidadTotal = document.querySelector('.cantidad-total');
    const checkboxesSabores = document.querySelectorAll('.lista-pizzas .check');

    // === 2. CONFIGURACIÓN DE PRECIOS Y VARIABLES ===
    const preciosPorTamano = {
        "pequeña": 15000,
        "mediana": 25000,
        "grande": 35000,
        "extragande": 45000
    };
    const VALOR_ADICIONAL_EXTRA = 8000;
    let cantidadDePizzas = 1;

    // === 3. FUNCIÓN DE VALIDACIÓN DE COMBINACIONES ===
    function validarCombinaciones(event) {
        const tamano = selectTamano.value;
        const seleccionados = document.querySelectorAll('.lista-pizzas .check:checked');
        const cantidadSeleccionada = seleccionados.length;

        // Definir límites de sabores según el tamaño
        let limite = 0;
        let mensaje = "";

        if (tamano === "pequeña") {
            limite = 0;
            mensaje = "La pizza Pequeña no permite combinar sabores adicionales.";
        } else if (tamano === "mediana") {
            limite = 1;
            mensaje = "La pizza Mediana solo permite elegir 1 sabor adicional.";
        } else if (tamano === "grande") {
            limite = 3;
            mensaje = "La pizza Grande solo permite hasta 3 sabores adicionales.";
        } else if (tamano === "extragande") {
            limite = 4;
            mensaje = "La pizza Extragrande permite un máximo de 4 sabores.";
        }

        // SI EL USUARIO INTENTA MARCAR MÁS DEL LÍMITE:
        if (cantidadSeleccionada > limite) {
            // Solo mostramos alerta si el usuario está intentando marcar un checkbox (evento change)
            if (event && event.type === 'change' && event.target.checked) {
                alert(mensaje);
                event.target.checked = false; // Desmarcar inmediatamente
            } 
            // Si el exceso se debe a un cambio de tamaño, simplemente no permitimos el estado inválido
            else if (cantidadSeleccionada > limite) {
                 // Esto se maneja limpiando los checkbox al cambiar tamaño (ver abajo)
            }
            return false;
        }

        // BLOQUEO VISUAL: Si ya llegó al límite, deshabilitamos los no marcados
        checkboxesSabores.forEach(check => {
            if (!check.checked) {
                // Se deshabilitan si ya alcanzó el límite o si el límite es 0
                check.disabled = (cantidadSeleccionada >= limite);
            } else {
                // Los marcados siempre habilitados para poder desmarcarlos
                check.disabled = false;
            }
        });

        return true;
    }

    // === 4. FUNCIÓN PRINCIPAL DE CÁLCULO ===
    function calcularTotal(event) {
        // Primero validamos reglas
        validarCombinaciones(event);

        // A. Precio Base por tamaño
        let precioUnidad = preciosPorTamano[selectTamano.value] || 0;
        if (displayPrecioBase) {
            displayPrecioBase.textContent = `$${precioUnidad.toLocaleString()}`;
        }

        // B. Sumar Adicionales (Queso, Piña, etc.)
        itemsAdicionales.forEach(item => {
            const span = item.querySelector('.cantidad');
            const cant = parseInt(span.textContent || span.innerText);
            
            precioUnidad += cant * VALOR_ADICIONAL_EXTRA;
            
            // Feedback visual
            item.style.backgroundColor = cant > 0 ? "#fff3cd" : "transparent";
            item.style.borderRadius = "8px";
        });

        // C. Sumar Sabores Combinados (Checkboxes)
        const saboresMarcados = document.querySelectorAll('.lista-pizzas .check:checked');
        saboresMarcados.forEach(check => {
            // Extraer precio del texto (ej: "$ 8.000" -> 8000)
            const precioTexto = check.parentElement.querySelector('.precio').textContent;
            const valorSabor = parseInt(precioTexto.replace(/[^0-9]/g, ''));
            precioUnidad += valorSabor;
        });

        // D. Calcular Total Final
        const granTotal = precioUnidad * cantidadDePizzas;
        
        // E. Actualizar Interfaz
        displayCantidadTotal.textContent = cantidadDePizzas;
        displayPrecioFinal.textContent = `$${granTotal.toLocaleString()}`;
    }

    // === 5. ASIGNACIÓN DE EVENTOS ===

    // -- Botones de Adicionales (+ / -) --
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

    // -- Botones de Cantidad Total de Pizzas --
    btnMasTotal.addEventListener('click', () => {
        cantidadDePizzas++;
        calcularTotal();
    });

    btnMenosTotal.addEventListener('click', () => {
        if (cantidadDePizzas > 1) {
            cantidadDePizzas--;
            calcularTotal();
        }
    });

    // -- Cambio de Tamaño de Pizza --
    selectTamano.addEventListener('change', (e) => {
        // Al cambiar tamaño, reseteamos los sabores seleccionados para evitar incoherencias
        // (ej: pasar de Grande con 3 sabores a Pequeña)
        checkboxesSabores.forEach(c => {
            c.checked = false;
            c.disabled = false;
        });
        calcularTotal(e);
    });

    // -- Checkboxes de Sabores --
    checkboxesSabores.forEach(check => {
        check.addEventListener('change', (e) => calcularTotal(e));
    });

    // === 6. LÓGICA DEL BOTÓN AÑADIR (REDIRECCIÓN) ===
    botonAnadir.addEventListener('click', () => {
        // 1. Recolectar la información
        const nombrePizza = document.querySelector('h2').innerText;
        const tamano = selectTamano.value;
        const precioTotal = displayPrecioFinal.innerText;

        // 2. Obtener lista de adicionales
        let listaAdicionales = [];
        itemsAdicionales.forEach(item => {
            const cant = item.querySelector('.cantidad').innerText;
            if (parseInt(cant) > 0) {
                const nombre = item.querySelector('label').innerText;
                listaAdicionales.push(`${nombre} (x${cant})`);
            }
        });

        // 3. Obtener lista de sabores combinados
        let listaSabores = [];
        document.querySelectorAll('.lista-pizzas .check:checked').forEach(check => {
            listaSabores.push(check.parentElement.querySelector('label').innerText);
        });

        // 4. Crear objeto del pedido
        const miPedido = {
            producto: nombrePizza,
            tamano: tamano,
            cantidad: cantidadDePizzas,
            precio: precioTotal,
            adicionales: listaAdicionales,
            sabores: listaSabores
        };

        // 5. Guardar en LocalStorage y Redirigir
        // Guardamos el objeto como string JSON
        localStorage.setItem('pedido_cliente', JSON.stringify(miPedido));
        
        // Redirigimos a la ruta creada en Flask
        window.location.href = "/resumen_pedido";
    });

    // Inicialización al cargar la página
    calcularTotal();
});