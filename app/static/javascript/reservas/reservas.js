const API_RESERVAS = '/api/';

export async function inicio() { window.location.href = '/menu'; }

export function prepararPaso1Reserva() {
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


export async function cargarTematicas() {
    const select = document.getElementById('v_tematica');
    if (!select) return;
    try {
        const res = await fetch(API_RESERVAS + 'tematicas');
        const data = await res.json();
        select.innerHTML = '<option value="" disabled selected>Selecciona una temática...</option>';
        data.forEach(t => {
            const option = document.createElement('option');
            option.value = t.tematica_id;
            option.textContent = t.nombre_tematica;
            select.appendChild(option);
        });
    } catch (error) { console.error("Error cargando temáticas", error); }
}

export function prepararPaso2() {
    const form = document.getElementById('form-reserva');
    if (!form) return;
    form.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn-submit');
        btn.disabled = true;
        btn.innerText = "PROCESANDO...";

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
    const qrData = localStorage.getItem('qr_reserva');
    if (img && qrData) img.src = `data:image/png;base64,${qrData}`;
}