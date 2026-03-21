/* ── Gestión de Mesas ── */

let mesasCache = [];
let _pisoFiltroActual = '';

async function cargarMesas() {
    const tbody = document.getElementById('tbody-mesas');
    tbody.innerHTML = '<tr><td colspan="4" class="cargando">Cargando...</td></tr>';
    try {
        mesasCache = await apiFetch('/admin/api/mesas');
        renderizarMesas();
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function renderizarMesas() {
    const tbody = document.getElementById('tbody-mesas');
    const lista = _pisoFiltroActual
        ? mesasCache.filter(m => String(m.piso) === _pisoFiltroActual)
        : mesasCache;
    if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="cargando">Sin mesas para el filtro seleccionado</td></tr>';
        return;
    }
    tbody.innerHTML = lista.map(m => `
        <tr>
            <td>${m.mesa_id}</td>
            <td>${esc(String(m.numero_mesa || m.mesa_id))}</td>
            <td>Piso ${m.piso}</td>
            <td>
                <button class="btn-accion azul" onclick="editarMesa(${m.mesa_id})">Editar</button>
                <button class="btn-accion rojo"  onclick="eliminarMesa(${m.mesa_id})">Eliminar</button>
            </td>
        </tr>
    `).join('');
}

function filtrarMesasPorPiso(btn) {
    _pisoFiltroActual = btn.dataset.piso;
    document.querySelectorAll('.btn-filtro-piso').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    renderizarMesas();
}

function abrirModalMesa() {
    document.getElementById('form-mesa').reset();
    document.getElementById('fm-id').value = '';
    document.getElementById('fm-piso').value = '1';
    document.getElementById('modal-mesa-titulo').textContent = 'Nueva Mesa';
    document.getElementById('modal-mesa').classList.remove('oculta');
    document.getElementById('fm-numero').focus();
}

function cerrarModalMesa() {
    document.getElementById('modal-mesa').classList.add('oculta');
}

function editarMesa(id) {
    const mesa = mesasCache.find(m => m.mesa_id === id);
    if (!mesa) { toast('Mesa no encontrada', 'error'); return; }
    document.getElementById('fm-id').value       = mesa.mesa_id;
    document.getElementById('fm-numero').value   = mesa.numero_mesa || mesa.mesa_id;
    document.getElementById('fm-piso').value     = mesa.piso;
    document.getElementById('modal-mesa-titulo').textContent = 'Editar Mesa';
    document.getElementById('modal-mesa').classList.remove('oculta');
    document.getElementById('fm-numero').focus();
}

async function guardarMesa(e) {
    e.preventDefault();
    const id = document.getElementById('fm-id').value;
    const payload = {
        numero_mesa: parseInt(document.getElementById('fm-numero').value),
        piso:        parseInt(document.getElementById('fm-piso').value),
    };
    try {
        if (id) {
            await apiFetch(`/admin/api/mesas/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
            toast('Mesa actualizada');
        } else {
            await apiFetch('/admin/api/mesas', { method: 'POST', body: JSON.stringify(payload) });
            toast('Mesa creada');
        }
        cerrarModalMesa();
        cargarMesas();
    } catch (e2) {
        toast(e2.message, 'error');
    }
}

async function eliminarMesa(id) {
    const mesa = mesasCache.find(m => m.mesa_id === id);
    const label = mesa ? `Mesa ${mesa.numero_mesa} – Piso ${mesa.piso}` : `#${id}`;
    if (!confirm(`¿Eliminar "${label}"? Esta acción no se puede deshacer.`)) return;
    try {
        await apiFetch(`/admin/api/mesas/${id}`, { method: 'DELETE' });
        toast('Mesa eliminada');
        cargarMesas();
    } catch (e) {
        toast(e.message, 'error');
    }
}
