document.addEventListener('DOMContentLoaded', () => {
    // === 1. SELECCIÓN DE ELEMENTOS DEL DOM ===
    const selectTamano = document.querySelector('.tamano-pizza');
    const displayPrecioBase = document.querySelector('.precio-btn');
    const displayPrecioFinal = document.querySelector('.precio-fn');
    const itemsAdicionales = document.querySelectorAll('.adicion-item');
    const botonAnadir = document.querySelector('.añadir');
    const btnMasTotal = document.querySelector('.cont_btn-mas');
    const btnMenosTotal = document.querySelector('.cont_btn-menos');
    const displayCantidadTotal = document.querySelector('.cantidad-total');
    const checkboxesSabores = document.querySelectorAll('.lista-pizzas .check');

    // === 2. CONFIGURACIÓN DE PRECIOS Y VARIABLES ===
    const preciosPorTamano = {
        "pequeña": 15000,
        "mediana": 25000,
        "grande": 35000,
        "extragande": 45000 // Mantengo "extragande" como está en tu HTML
    };
    const VALOR_ADICIONAL_EXTRA = 8000;
    let cantidadDePizzas = 1;

    // === 3. FUNCIÓN DE VALIDACIÓN DE COMBINACIONES ===
    function validarCombinaciones(event) {
        const tamano = selectTamano.value;
        const seleccionados = document.querySelectorAll('.lista-pizzas .check:checked');
        const cantidadSeleccionada = seleccionados.length;

        // Definir límites según tu regla
        let limite = 0;
        if (tamano === "pequeña") limite = 0;
        else if (tamano === "mediana") limite = 1;
        else if (tamano === "grande") limite = 3;
        else if (tamano === "extragande") limite = 4;

        // Si el usuario intenta marcar uno más del límite
        if (cantidadSeleccionada > limite) {
            if (limite === 0) {
                alert("La pizza Pequeña no permite combinar sabores adicionales.");
            } else {
                alert(`Para el tamaño ${tamano} solo puedes elegir hasta ${limite} sabor(es) adicionales.`);
            }
            
            // Desmarcamos el que acaba de presionar
            if (event && event.target) {
                event.target.checked = false;
            }
            return false; // Indica que la validación falló
        }

        // Bloqueo visual de los que quedan libres si ya llegó al límite
        checkboxesSabores.forEach(check => {
            if (!check.checked) {
                check.disabled = (cantidadSeleccionada >= limite && limite > 0) || (limite === 0);
            }
        });
        
        return true;
    }

    // === 4. FUNCIÓN PRINCIPAL DE CÁLCULO ===
    function calcularTotal(event) {
        // Primero validamos si puede marcar ese sabor
        validarCombinaciones(event);

        // A. Precio Base por tamaño
        let precioUnidad = preciosPorTamano[selectTamano.value] || 0;
        displayPrecioBase.textContent = `$${precioUnidad.toLocaleString()}`;

        // B. Sumar Adicionales (Ingredientes extra como Queso, Piña)
        itemsAdicionales.forEach(item => {
            const cant = parseInt(item.querySelector('.cantidad').textContent);
            precioUnidad += cant * VALOR_ADICIONAL_EXTRA;
            
            // Cambio de color visual si hay adiciones
            item.style.backgroundColor = cant > 0 ? "#fff3cd" : "transparent";
            item.style.borderRadius = "8px";
        });

        // C. Sumar Sabores Combinados (Checkboxes)
        checkboxesSabores.forEach(check => {
            if (check.checked) {
                // Extraemos el número del texto "$8000" o "$17500"
                const precioTexto = check.parentElement.querySelector('.precio').textContent;
                const valorSabor = parseInt(precioTexto.replace(/[^0-9]/g, ''));
                precioUnidad += valorSabor;
            }
        });

        // D. Multiplicar por cantidad de pizzas (Footer)
        const granTotal = precioUnidad * cantidadDePizzas;
        
        // E. Actualizar Interfaz
        displayCantidadTotal.textContent = cantidadDePizzas;
        displayPrecioFinal.textContent = `$${granTotal.toLocaleString()}`;
    }

    // === 5. ASIGNACIÓN DE EVENTOS ===

    // Eventos para Adicionales (Botones + y -)
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

    // Eventos para Cantidad de Pizzas (Footer)
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

    // Evento para cambio de Tamaño
    selectTamano.addEventListener('change', () => {
        // Si cambia a un tamaño menor, reseteamos los sabores para evitar errores de lógica
        checkboxesSabores.forEach(c => c.checked = false);
        calcularTotal();
    });

    // Evento para Checkboxes de sabores
    checkboxesSabores.forEach(check => {
        check.addEventListener('change', (e) => calcularTotal(e));
    });
    // === FUNCIÓN DE VALIDACIÓN DE COMBINACIONES (ACTUALIZADA) ===
function validarCombinaciones(event) {
    const tamano = selectTamano.value;
    const seleccionados = document.querySelectorAll('.lista-pizzas .check:checked');
    const cantidadSeleccionada = seleccionados.length;

    // Definir límites según tu regla exacta
    let limite = 0;
    let mensaje = "";

    if (tamano === "pequeña") {
        limite = 0;
        mensaje = "La pizza Pequeña no permite combinar sabores.";
    } else if (tamano === "mediana") {
        limite = 1;
        mensaje = "La pizza Mediana solo permite elegir 1 sabor adicional.";
    } else if (tamano === "grande") {
        limite = 2;
        mensaje = "La pizza Grande solo permite hasta 3 sabores adicionales.";
    } else if (tamano === "extragande") {
        limite = 4;
        mensaje = "La pizza Extragrande permite un máximo de 4 sabores.";
    }

    // SI EL USUARIO INTENTA MARCAR UNO CUANDO NO DEBE:
    if (cantidadSeleccionada > limite) {
        // 1. Mostrar el mensaje de advertencia
        alert(mensaje);
        
        // 2. Desmarcar el checkbox que el usuario acaba de tocar
        if (event && event.target) {
            event.target.checked = false;
        }
        return false;
    }

    // BLOQUEO VISUAL: Si ya llegó al límite, ponemos en gris los otros cuadritos
    checkboxesSabores.forEach(check => {
        if (!check.checked) {
            // Se deshabilitan si ya alcanzó el límite o si el tamaño es pequeña (límite 0)
            check.disabled = (cantidadSeleccionada >= limite);
        } else {
            // Los que ya están marcados siempre deben estar activos para poder quitarlos
            check.disabled = false;
        }
    });

    return true;
    
}

    // Inicialización al cargar la página
    calcularTotal();
    // Busca el botón por su clase "añadir"
botonAnadir.addEventListener('click', () => {
    // 1. Recolectar la información
    const nombrePizza = document.querySelector('h2').innerText;
    const tamano = document.querySelector('.tamano-pizza').value;
    const cantPizzas = document.querySelector('.cantidad-total').innerText;
    const precioTotal = document.querySelector('.precio-fn').innerText;

    // 2. Obtener lista de adicionales (Extra Queso, Piña, etc.)
    let listaAdicionales = [];
    document.querySelectorAll('.adicion-item').forEach(item => {
        const cant = item.querySelector('.cantidad').innerText;
        if (parseInt(cant) > 0) {
            const nombre = item.querySelector('label').innerText;
            listaAdicionales.push(`${nombre} (x${cant})`);
        }
    });

    // 3. Obtener lista de sabores combinados (Pepperoni, Hawaiana, etc.)
    let listaSabores = [];
    document.querySelectorAll('.lista-pizzas .check:checked').forEach(check => {
        listaSabores.push(check.parentElement.querySelector('label').innerText);
    });

    // 4. Construir el mensaje final
    let mensajeResumen = `Haz añadido: ${cantPizzas} ${nombrePizza} (${tamano})\n`;
    
    if (listaSabores.length > 0) {
        mensajeResumen += `\n🍕 Sabores combinados: ${listaSabores.join(', ')}`;
    }

    if (listaAdicionales.length > 0) {
        mensajeResumen += `\n➕ Adicionales: ${listaAdicionales.join(', ')}`;
    }

    mensajeResumen += `\n\n💰 TOTAL A PAGAR: ${precioTotal}`;

    // 5. Mostrar el mensaje
    alert(mensajeResumen);

    // Aquí iría el envío al backend (fetch)
    console.log("Objeto enviado al backend:", {
        nombrePizza, tamano, cantPizzas, precioTotal, listaAdicionales, listaSabores
    });
});
    
});