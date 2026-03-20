/* ── Gestión de Temáticas (admin) ── */

async function cargarTematicas() {
    const tbody = document.getElementById('tbody-tematicas');
    tbody.innerHTML = '<tr><td colspan="4" class="cargando">Cargando...</td></tr>';
    try {
        const tematicas = await apiFetch('/admin/api/tematicas');
        if (!tematicas.length) {
            tbody.innerHTML = '<tr><td colspan="4" class="cargando">Sin temáticas registradas</td></tr>';
            return;
        }
        tbody.innerHTML = tematicas.map(t => {
            const activo = t.activo === undefined ? 1 : t.activo;
            return `
            <tr>
                <td>${t.tematica_id}</td>
                <td>${esc(t.nombre_tematica)}</td>
                <td><span class="pill ${activo ? 'verde' : 'rojo'}">${activo ? 'Activa' : 'Inactiva'}</span></td>
                <td style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button class="btn-accion ${activo ? 'gris' : 'verde'}"
                        onclick="toggleTematica(${t.tematica_id}, ${activo})">
                        ${activo ? 'Desactivar' : 'Activar'}
                    </button>
                    <button class="btn-accion rojo"
                        onclick="eliminarTematica(${t.tematica_id}, '${esc(t.nombre_tematica)}')">
                        Eliminar
                    </button>
                </td>
            </tr>`;
        }).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="4" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

async function toggleTematica(id, activoActual) {
    const nuevo = activoActual ? 0 : 1;
    try {
        await apiFetch(`/admin/api/tematicas/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ activo: nuevo }),
        });
        toast(nuevo ? 'Temática activada' : 'Temática desactivada');
        cargarTematicas();
    } catch (e) {
        toast(e.message, 'error');
    }
}

async function agregarTematica(e) {
    e.preventDefault();
    const nombre = document.getElementById('ft-nombre').value.trim();
    if (!nombre) return;
    try {
        await apiFetch('/admin/api/tematicas', {
            method: 'POST',
            body: JSON.stringify({ nombre_tematica: nombre }),
        });
        toast('Temática agregada');
        document.getElementById('ft-nombre').value = '';
        cargarTematicas();
    } catch (e) {
        toast(e.message, 'error');
    }
}

async function eliminarTematica(id, nombre) {
    if (!confirm(`¿Eliminar la temática "${nombre}"?`)) return;
    try {
        await apiFetch(`/admin/api/tematicas/${id}`, { method: 'DELETE' });
        toast('Temática eliminada');
        cargarTematicas();
    } catch (e) {
        toast(e.message, 'error');
    }
}
