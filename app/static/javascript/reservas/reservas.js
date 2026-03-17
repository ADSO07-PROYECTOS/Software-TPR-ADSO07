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
        
        window.location.replace('/detalles_reserva'); 
    };
}

export function hora(){
    const HORAS_DISPONIBLES = [16,17,18,19,20,21,22,23];
    return HORAS_DISPONIBLES.map(h => {
                const ampm = h < 12 ? 'AM' : 'PM';
                const h12 = h % 12 === 0 ? 12 : h % 12;
                return {
                    label: `${h12}:00 ${ampm}`,
                    valor: `${String(h).padStart(2,'0')}:00`
                };
            });
}

export function abrirModalHoraReserva() {
            const grid = document.getElementById('horas_grid_reserva');
            grid.innerHTML = '';
            const fechaInput = document.getElementById('v_fec').value;
            const hoy = new Date();
            const hoySolo = hoy.toISOString().split('T')[0];
            const esHoy = fechaInput === hoySolo;
            const horaActual = hoy.getHours();
            const valorActual = document.getElementById('v_hor').value;

            hora().forEach(bloque => {
                const h = parseInt(bloque.valor);
                const bloqueada = esHoy && h <= horaActual;
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.textContent = bloque.label;
                btn.className = 'chip-hora';

                if (bloqueada) {
                    btn.classList.add('chip-bloqueada');
                    btn.disabled = true;
                } else {
                    if (bloque.valor === valorActual) btn.classList.add('chip-activa');
                    btn.addEventListener('click', () => seleccionarHoraReserva(bloque.label, bloque.valor));
                }
                grid.appendChild(btn);
});
            document.getElementById('modal_hora_reserva').classList.remove('oculto-hora');
}

export function seleccionarHoraReserva(label, valor) {
            document.getElementById('v_hor').value = valor;
            document.getElementById('hora_display_reserva').textContent = label;
            cerrarModalHoraReserva();
        }

export function cerrarModalHoraReserva() {
            document.getElementById('modal_hora_reserva').classList.add('oculto-hora');
        }

       

export async function cargarTematicas() {
    const select = document.getElementById('v_tematica');
    if (!select) return;

    const tieneOpcionesIniciales = select.options.length > 1;

    try {
        const res = await fetch(API_RESERVAS + 'tematicas');
        if (!res.ok) throw new Error('No se pudieron obtener temáticas');
        const data = await res.json();

        const lista = Array.isArray(data)
            ? data
            : (Array.isArray(data.tematicas) ? data.tematicas : []);

        if (!lista.length) {
            if (!tieneOpcionesIniciales) {
                select.innerHTML = '<option value="" disabled selected>No hay temáticas disponibles</option>';
            }
            return;
        }

        select.innerHTML = '<option value="" disabled selected>Selecciona una temática...</option>';
        lista.forEach(t => {
            const option = document.createElement('option');
            option.value = t.tematica_id;
            option.textContent = t.nombre_tematica;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error cargando temáticas', error);
        if (!tieneOpcionesIniciales) {
            select.innerHTML = '<option value="" disabled selected>Error al cargar temáticas</option>';
        }
    }
}

export function prepararPaso2() {
    const form = document.getElementById('form-reserva');
    if (!form) return;
    form.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn-submit');
        btn.disabled = true;
        btn.innerText = "PROCESANDO...";

        let clienteTemporal = null;
        try {
            clienteTemporal = JSON.parse(localStorage.getItem('cliente_temporal') || 'null');
        } catch (_e) {
            clienteTemporal = null;
        }

        if (!clienteTemporal || !clienteTemporal.doc || !clienteTemporal.nom) {
            alert('No se encontraron los datos del cliente. Vuelve al paso anterior e inténtalo de nuevo.');
            btn.disabled = false;
            btn.innerText = 'RESERVAR';
            return;
        }

        const payload = {
            cliente: clienteTemporal,
            reserva: {
                fec: form.fec.value,
                hor: form.hor.value,
                hor_label: document.getElementById('hora_display_reserva')?.textContent || form.hor.value,
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

            let data = {};
            try {
                data = await res.json();
            } catch (_e) {
                data = {};
            }

            if (res.ok && data.status === 'success') {
                localStorage.setItem('qr_reserva', data.qr);
                localStorage.setItem('id_reserva', data.id);

                const carritoItems = JSON.parse(localStorage.getItem('carrito_tpr')) || [];
                const totalReserva = carritoItems.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
                localStorage.setItem('total_reserva', totalReserva);

                localStorage.removeItem('carrito');
                localStorage.removeItem('carrito_tpr');

                const metodo_pago = payload.reserva.metodo_pago;
                if (metodo_pago === '1') {
                    window.location.href = '/subir_comprobante';
                } else {
                    window.location.href = '/exito';
                }
            } else {
                const mensaje = data.message || data.msg || data.error || 'No fue posible procesar la reserva.';
                alert('Error: ' + mensaje);
                btn.disabled = false;
                btn.innerText = 'RESERVAR';
            }
        } catch (error) {
            alert('Error de conexión con el microservicio de reservas');
            btn.disabled = false;
            btn.innerText = 'RESERVAR';
        }
    };
}

export function mostrarResultadoFinal(){
    const img = document.getElementById('qr-img');
    const qrData = localStorage.getItem('qr_reserva');
    if (img && qrData) {
        img.src = `data:image/png;base64,${qrData}`;
}
};
