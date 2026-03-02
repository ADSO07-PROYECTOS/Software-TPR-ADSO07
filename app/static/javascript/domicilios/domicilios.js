const API_DOMICILIOS = 'http://127.0.0.1:5006/api/domicilios'; 

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('datos_cliente')) {
        prepararPaso1();
    } else if (path.includes('direccion_domicilio')) {
        prepararPasoDomicilio();
    }
    // ... resto de tus condiciones (reserva, exito, etc.)
});

// MODIFICACIÓN EN PASO 1:
function prepararPaso1() {
    const form = document.getElementById('form-paso1');
    if (!form) return;

    form.onsubmit = (e) => {
        e.preventDefault();
        const cliente = {
            nom: form.nom.value,
            doc: form.doc.value,
            correo: form.correo.value,
            tel: form.tel.value
        };
        localStorage.setItem('cliente_temporal', JSON.stringify(cliente));
        
        // LÓGICA DE REDIRECCIÓN:
        // Si el usuario viene del carrito de domicilios, va a dirección. 
        // Si viene de reserva de mesa, va a detalles_reserva.
        const tipoFlujo = localStorage.getItem('flujo_actual'); // 'domicilio' o 'reserva'
        if (tipoFlujo === 'domicilio') {
            window.location.href = '/direccion_domicilio';
        } else {
            window.location.href = '/detalles_reserva';
        }
    };
}

// NUEVO: Lógica para enviar el domicilio
function prepararPasoDomicilio() {
    const form = document.getElementById('form-domicilio');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn-submit-dom');
        btn.disabled = true;
        btn.innerText = "PROCESANDO...";

        const payload = {
            cliente: JSON.parse(localStorage.getItem('cliente_temporal')),
            domicilio: {
                direccion: form.direccion.value,
                referencia: form.referencia.value,
                metodo_pago: form.metodo_pago.value
            },
            productos: JSON.parse(localStorage.getItem('carrito_tpr')) || []
        };

        try {
            const res = await fetch(API_DOMICILIOS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.status === 'success') {
                localStorage.setItem('id_orden', data.id);
                window.location.href = '/exito_domicilio';
            } else {
                alert("Error: " + data.message);
                btn.disabled = false;
            }
        } catch (error) {
            alert("Error conectando con el servicio de domicilios");
            btn.disabled = false;
        }
    };
}