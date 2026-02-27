const API_RESERVAS = 'http://127.0.0.1:5005/api/';


document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('datos_cliente')) {
        prepararPaso1();
    } else if (path.includes('detalles_reserva')) {
        cargarTematicas(); 
        prepararPaso2();
    } else if (path.includes('exito')) {
        mostrarResultadoFinal();
    }
});

export async function inicio() {
    window.location.href = '/menu';
};
    

export async function cargarTematicas() {
    const select = document.getElementById('v_tematica');
    if (!select) return;
    try {
        const res = await fetch(API_RESERVAS + 'tematicas');
        if (!res.ok) throw new Error("Error en la respuesta del servidor");
        
        const data = await res.json(); 

        select.innerHTML = '<option value="" disabled selected>Selecciona una temática...</option>';

        data.forEach(t => {
            const option = document.createElement('option');
            option.value = t.tematica_id;
            option.textContent = t.nombre_tematica;
            select.appendChild(option);
        });

    } catch (e) {
        console.error("Error cargando temáticas:", e);
        select.innerHTML = '<option value="1">General (Error al cargar)</option>';
    }
}


export function prepararPaso1() {
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
        window.location.href = '/detalles_reserva';
    };
}

export function prepararPaso2() {
    const form = document.getElementById('form-final');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn-submit');
        btn.disabled = true;
        btn.innerText = "PROCESANDO...";

        // Consolidar toda la información
        const payload = {
            cliente: JSON.parse(localStorage.getItem('cliente_temporal')),
            reserva: {
                fec: form.fec.value,
                hor: form.hor.value,
                hor_label: form.hor.options[form.hor.selectedIndex].text,
                tematica: form.tematica.value,
                personas: form.personas.value,
                piso: form.piso.value,
                metodo_pago: form.metodo_pago.value
            },
            pedido: JSON.parse(localStorage.getItem('carrito_tpr')) || []
        };

        try {
            const res = await fetch(API_RESERVAS + 'reservas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.status === 'success') {
                localStorage.setItem('qr_reserva', data.qr);
                localStorage.setItem('id_reserva', data.id);
                window.location.href = '/exito';
            } else {
                alert("Error: " + data.message);
                btn.disabled = false;
            }
        } catch (error) {
            alert("Error de conexión con el microservicio de reservas");
            btn.disabled = false;
        }
    };
}

export function mostrarResultadoFinal() {
    const img = document.getElementById('qr-img');
    const msg = document.getElementById('mensaje-exito');
    const qrData = localStorage.getItem('qr_reserva');

    if (img && qrData) {
        img.src = `data:image/png;base64,${qrData}`;
        msg.innerText = `¡Tu reserva ha sido creada con éxito! Revisa tu correo electrónico.`;
        // Opcional: limpiar localStorage
        localStorage.removeItem('qr_reserva');
        localStorage.removeItem('id_reserva');
    }
}