/* ── Modal de comprobantes de pago ── */

async function abrirModalComprobante(id, tipo = 'reserva') {
    try {
        let registro;
        if (tipo === 'domicilio') {
            const domicilios = await apiFetch('/admin/api/domicilios');
            registro = domicilios.find(d => d.domicilio_id === id);
        } else {
            const reservas = await apiFetch('/admin/api/reservas');
            registro = reservas.find(r => r.reserva_id === id);
        }

        if (!registro || !registro.comprobante_transferencia) {
            alert('Comprobante no encontrado');
            return;
        }

        const modal       = document.getElementById('modal-comprobante');
        const img         = document.getElementById('comprobante-preview');
        const enlace      = document.getElementById('comprobante-enlace');
        const titulo      = document.querySelector('#modal-comprobante .modal-header h2');
        const btnConfirmar = document.getElementById('btn-confirmar-comprobante');
        const btnRechazar  = document.getElementById('btn-rechazar-comprobante');

        const label = tipo === 'domicilio' ? `Pedido #${id}` : `Reserva #${id} - ${registro.cc_cliente}`;
        titulo.textContent = `Comprobante ${label}`;

        const rutaComprobante = `/static/${registro.comprobante_transferencia}`;

        if (registro.comprobante_transferencia.endsWith('.pdf')) {
            img.style.display = 'none';
            enlace.href = rutaComprobante;
            enlace.style.display = 'block';
            enlace.textContent = '📄 Ver PDF en nueva ventana';
        } else {
            img.src = rutaComprobante;
            img.style.display = 'block';
            enlace.style.display = 'none';
        }

        btnConfirmar.dataset.reservaId = id;
        btnConfirmar.dataset.tipo = tipo;
        btnRechazar.dataset.reservaId  = id;
        btnRechazar.dataset.tipo  = tipo;
        modal.classList.remove('oculta');
    } catch (e) {
        alert('Error al abrir comprobante: ' + e.message);
    }
}

function cerrarModalComprobante() {
    document.getElementById('modal-comprobante').classList.add('oculta');
}

async function rechazarComprobante(reservaId) {
    const btn  = document.getElementById('btn-rechazar-comprobante');
    const tipo = btn.dataset.tipo || 'reserva';
    if (!confirm('¿Rechazar este comprobante? El pedido/reserva volverá a estado Pendiente.')) return;

    try {
        btn.disabled = true;
        btn.textContent = 'RECHAZANDO...';

        if (tipo === 'domicilio') {
            await apiFetch(`/admin/api/domicilios/${reservaId}`, {
                method: 'PUT',
                body: JSON.stringify({ estado_pedido: 'Pendiente', comprobante_validado: true }),
            });
        } else {
            await apiFetch(`/admin/api/reservas/${reservaId}`, {
                method: 'PUT',
                body: JSON.stringify({ estado: 'pendiente', comprobante_validado: true }),
            });
        }

        cerrarModalComprobante();
        toast(`✗ Comprobante rechazado. Volvió a Pendiente.`, 'error');
        tipo === 'domicilio' ? cargarPedidos() : cargarReservas();
    } catch (e) {
        alert('Error: ' + e.message);
        btn.disabled = false;
        btn.textContent = '✗ RECHAZAR';
    }
}

async function confirmarComprobante(reservaId) {
    const btn  = document.getElementById('btn-confirmar-comprobante');
    const tipo = btn.dataset.tipo || 'reserva';
    if (!confirm('¿Confirmar este comprobante de transferencia?')) return;
    
    try {
        btn.disabled = true;
        btn.textContent = 'CONFIRMANDO...';

        if (tipo === 'domicilio') {
            await apiFetch(`/admin/api/domicilios/${reservaId}`, {
                method: 'PUT',
                body: JSON.stringify({ estado_pedido: 'En preparación', comprobante_validado: true }),
            });
        } else {
            await apiFetch(`/admin/api/reservas/${reservaId}`, {
                method: 'PUT',
                body: JSON.stringify({ estado: 'confirmada', comprobante_validado: true }),
            });
        }

        cerrarModalComprobante();
        toast(`✓ Comprobante validado.`);
        tipo === 'domicilio' ? cargarPedidos() : cargarReservas();
    } catch (e) {
        alert('Error: ' + e.message);
        btn.disabled = false;
        btn.textContent = '✓ CONFIRMAR PAGO';
    }
}
