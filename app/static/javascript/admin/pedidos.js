/* ── Gestión de Pedidos / Domicilios ── */

const ESTADOS_DOMICILIO = ['Pendiente', 'En preparación', 'Listo', 'Entregado', 'Cancelado'];

async function cargarPedidos() {
    const tbody = document.getElementById('tbody-pedidos');
    tbody.innerHTML = '<tr><td colspan="8" class="cargando">Cargando...</td></tr>';
    try {
        const domicilios = await apiFetch('/admin/api/domicilios');
        if (!domicilios.length) {
            tbody.innerHTML = '<tr><td colspan="8" class="cargando">Sin domicilios registrados</td></tr>';
            return;
        }
        tbody.innerHTML = domicilios.map(d => {
            const tieneComprobante = Boolean(d.comprobante_transferencia);
            let pagoCell;
            if (tieneComprobante) {
                pagoCell = `<span class="pill amarillo">⏳ EN REVISIÓN</span><br><button class="btn-accion azul" style="margin-top:4px; font-size:0.85rem;" onclick="abrirModalComprobante(${d.domicilio_id}, 'domicilio')">📄 Ver</button>`;
            } else {
                pagoCell = d.pago_transferencia ? '🏦 Transferencia' : '💵 Efectivo';
            }
            return `
            <tr>
                <td>${d.domicilio_id}</td>
                <td>${esc(d.nombre || '')}<br><small>${esc(d.telefono || '')}</small></td>
                <td>${esc(d.direccion || '')}</td>
                <td>$${d.total ? Number(d.total).toLocaleString('es-CO') : '0'}</td>
                <td>${pagoCell}</td>
                <td><small>${formatearHora(d.fecha_hora)}</small></td>
                <td><span class="pill ${pillDom(d.estado_pedido)}">${esc(d.estado_pedido || '')}</span></td>
                <td>
                    <select class="sel-estado" onchange="cambiarEstadoDomicilio(${d.domicilio_id}, this.value)">
                        ${ESTADOS_DOMICILIO.map(s =>
                            `<option value="${s}" ${s === d.estado_pedido ? 'selected' : ''}>${s}</option>`
                        ).join('')}
                    </select>
                </td>
            </tr>
        `}).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="8" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function pillDom(estado) {
    const mapa = {
        'Pendiente': 'amarillo', 'En preparación': 'azul',
        'Listo': 'naranja', 'Entregado': 'verde', 'Cancelado': 'rojo',
    };
    return mapa[estado] || 'gris';
}

async function cambiarEstadoDomicilio(id, nuevoEstado) {
    try {
        await apiFetch(`/admin/api/domicilios/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ estado_pedido: nuevoEstado }),
        });
        toast(`Pedido #${id} → ${nuevoEstado}`);
    } catch (e) {
        toast(e.message, 'error');
    }
}
