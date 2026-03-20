/* ── Gestión de Reservas (admin) ── */

const ESTADOS_RESERVA = ['en espera', 'confirmada', 'ocupada', 'cancelada', 'finalizada'];

async function cargarReservas() {
    const tbody = document.getElementById('tbody-reservas');
    tbody.innerHTML = '<tr><td colspan="10" class="cargando">Cargando...</td></tr>';
    try {
        const reservas = await apiFetch('/admin/api/reservas');
        if (!reservas.length) {
            tbody.innerHTML = '<tr><td colspan="10" class="cargando">Sin reservas registradas</td></tr>';
            return;
        }
        tbody.innerHTML = reservas.map(r => {
            const esTransferencia = Boolean(r.pago_transferencia || r.comprobante_transferencia);
            const tienePendiente = Boolean(r.comprobante_transferencia);
            const estadoActual = tienePendiente ? 'en espera' : (r.estado || '');
            return `
            <tr>
                <td>${r.reserva_id}</td>
                <td>${esc(r.nombre || '')}<br><small>${esc(r.telefono || '')}</small></td>
                <td><small>${formatearHora(r.fecha_hora)}</small></td>
                <td>${r.cantidad_personas}</td>
                <td>${r.piso || '—'}</td>
                <td>${esc(r.nombre_tematica || '—')}</td>
                <td>${esTransferencia ? '🏦 Transfer.' : '💵 Efectivo'}</td>
                <td>
                    ${tienePendiente 
                        ? `<span class="pill amarillo">⏳ PENDIENTE</span><br><button class="btn-accion azul" style="margin-top:4px; font-size:0.85rem;" onclick="abrirModalComprobante(${r.reserva_id})">📄 Ver</button>` 
                        : '✓ Confirmado'
                    }
                </td>
                <td>
                    <span class="pill ${pillRes(estadoActual)}">${esc(estadoActual)}</span>
                </td>
                <td>
                    <select class="sel-estado" onchange="cambiarEstadoReserva(${r.reserva_id}, this.value)">
                        ${ESTADOS_RESERVA.map(s =>
                            `<option value="${s}" ${s === estadoActual ? 'selected' : ''}>${s}</option>`
                        ).join('')}
                    </select>
                </td>
            </tr>
        `;
        }).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="10" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function pillRes(estado) {
    const mapa = {
        'en espera': 'amarillo', 'confirmada': 'verde', 'ocupada': 'azul',
        'cancelada': 'rojo', 'finalizada': 'gris',
    };
    return mapa[estado] || 'gris';
}

async function cambiarEstadoReserva(id, nuevoEstado) {
    try {
        await apiFetch(`/admin/api/reservas/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ estado: nuevoEstado }),
        });
        toast(`Reserva #${id} → ${nuevoEstado}`);
    } catch (e) {
        toast(e.message, 'error');
    }
}
