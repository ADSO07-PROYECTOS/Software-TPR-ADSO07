/* ── CRUD de Usuarios ── */

const ROLES_USUARIO = {
    cliente: 'Cliente',
    cajero: 'Cajero',
    administrador: 'Administrador',
};

let usuariosCache = [];
let _rolFiltroActual = '';

async function cargarUsuarios() {
    const tbody = document.getElementById('tbody-usuarios');
    tbody.innerHTML = '<tr><td colspan="7" class="cargando">Cargando...</td></tr>';
    try {
        usuariosCache = await apiFetch('/admin/api/usuarios');
        renderizarUsuarios();
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function renderizarUsuarios() {
    const tbody = document.getElementById('tbody-usuarios');
    const lista = _rolFiltroActual
        ? usuariosCache.filter(c => (c.rol || 'cliente') === _rolFiltroActual)
        : usuariosCache;
    if (!lista.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="cargando">Sin usuarios para el filtro seleccionado</td></tr>';
        return;
    }
    tbody.innerHTML = lista.map(c => `
        <tr>
            <td>${c.usuario_id}</td>
            <td>${esc(c.cc_usuario)}</td>
            <td>${esc(c.nombre)} ${esc(c.apellidos || '')}</td>
            <td>${esc(c.email || '')}</td>
            <td>${esc(c.telefono || '')}</td>
            <td><span class="pill ${pillRol(c.rol)}">${esc(formatearRol(c.rol))}</span></td>
            <td>
                <button class="btn-accion azul" onclick="editarUsuario(${c.usuario_id})">
                    Editar
                </button>
                <button class="btn-accion rojo" onclick="eliminarUsuario(${c.usuario_id})">
                    Eliminar
                </button>
            </td>
        </tr>
    `).join('');
}

function filtrarPorRol(btn) {
    _rolFiltroActual = btn.dataset.rol;
    document.querySelectorAll('.btn-filtro-rol').forEach(b => b.classList.remove('activo'));
    btn.classList.add('activo');
    renderizarUsuarios();
}

function formatearRol(rol) {
    return ROLES_USUARIO[rol] || 'Cliente';
}

function pillRol(rol) {
    const mapa = {
        administrador: 'rojo',
        cajero: 'azul',
        cliente: 'verde',
    };
    return mapa[rol] || 'gris';
}

function abrirModalUsuario() {
    document.getElementById('form-usuario').reset();
    document.getElementById('fu-id').value = '';
    document.getElementById('fu-rol').value = 'cajero';
    document.getElementById('fu-contrasena').required = true;
    document.getElementById('modal-usuario-titulo').textContent = 'Nuevo Usuario';
    document.getElementById('modal-usuario').classList.remove('oculta');
    document.getElementById('fu-cedula').focus();
}

function cerrarModalUsuario() {
    document.getElementById('modal-usuario').classList.add('oculta');
}

function editarUsuario(id) {
    const usuario = usuariosCache.find(item => item.usuario_id === id);
    if (!usuario) {
        toast('Usuario no encontrado', 'error');
        return;
    }
    document.getElementById('fu-id').value = usuario.usuario_id;
    document.getElementById('fu-cedula').value = usuario.cc_usuario || '';
    document.getElementById('fu-nombre').value = usuario.nombre || '';
    document.getElementById('fu-apellidos').value = usuario.apellidos || '';
    document.getElementById('fu-email').value = usuario.email || '';
    document.getElementById('fu-telefono').value = usuario.telefono || '';
    document.getElementById('fu-contrasena').value = '';
    document.getElementById('fu-contrasena').required = false;
    document.getElementById('fu-rol').value = usuario.rol || 'cajero';
    document.getElementById('modal-usuario-titulo').textContent = 'Editar Usuario';
    document.getElementById('modal-usuario').classList.remove('oculta');
    document.getElementById('fu-nombre').focus();
}

async function guardarUsuario(e) {
    e.preventDefault();
    const id = document.getElementById('fu-id').value;
    const payload = {
        cc_usuario:  document.getElementById('fu-cedula').value.trim(),
        nombre:      document.getElementById('fu-nombre').value.trim(),
        apellidos:   document.getElementById('fu-apellidos').value.trim(),
        email:       document.getElementById('fu-email').value.trim(),
        telefono:    document.getElementById('fu-telefono').value.trim(),
        rol:         document.getElementById('fu-rol').value,
        contrasena:  document.getElementById('fu-contrasena').value.trim(),
    };
    try {
        if (id) {
            await apiFetch(`/admin/api/usuarios/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            toast('Usuario actualizado');
        } else {
            await apiFetch('/admin/api/usuarios', {
                method: 'POST',
                body: JSON.stringify(payload),
            });
            toast('Usuario creado');
        }
        cerrarModalUsuario();
        cargarUsuarios();
    } catch (e2) {
        toast(e2.message, 'error');
    }
}

async function eliminarUsuario(id) {
    const usuario = usuariosCache.find(item => item.usuario_id === id);
    const nombre = usuario ? `${usuario.nombre} ${usuario.apellidos || ''}`.trim() : `#${id}`;
    if (!confirm(`¿Eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`)) return;
    try {
        await apiFetch(`/admin/api/usuarios/${id}`, { method: 'DELETE' });
        toast('Usuario eliminado');
        cargarUsuarios();
    } catch (e) {
        toast(e.message, 'error');
    }
}
