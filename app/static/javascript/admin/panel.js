

(function aplicarPermisosPorRol() {
    const ROL = document.body.dataset.rol || 'cajero';

    const PERMISOS = {
        administrador: ['dashboard', 'productos', 'pedidos', 'reservas', 'mesas', 'tematicas', 'usuarios'],
        cajero:        ['dashboard'],
    };
    const permitidas = PERMISOS[ROL] || ['dashboard'];

    document.querySelectorAll('.nav-btn[data-requiere-rol]').forEach(btn => {
        const seccion = btn.dataset.section;
        if (!permitidas.includes(seccion)) {
            btn.style.display = 'none';
        }
    });

    window._rolPermitidas = permitidas;
})();

(function () {
    const btnMenu    = document.getElementById('btn_menu');
    const sidebar    = document.getElementById('panel_izq');
    const overlay    = document.getElementById('sidebar-overlay');

    function abrirSidebar() {
        sidebar.classList.add('abierto');
        overlay.classList.add('visible');
    }
    function cerrarSidebar() {
        sidebar.classList.remove('abierto');
        overlay.classList.remove('visible');
    }

    btnMenu?.addEventListener('click', () => {
        sidebar.classList.contains('abierto') ? cerrarSidebar() : abrirSidebar();
    });
    overlay?.addEventListener('click', cerrarSidebar);
})();

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.section;

        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('.seccion').forEach(s => s.classList.remove('activa'));
        document.getElementById('sec-' + target).classList.add('activa');

        if (window.innerWidth <= 900) {
            document.getElementById('panel_izq').classList.remove('abierto');
            document.getElementById('sidebar-overlay').classList.remove('visible');
        }

        if (window._rolPermitidas && !window._rolPermitidas.includes(target)) return;

        if (target !== 'dashboard') cargarSeccion(target);
    });
});

function cargarSeccion(nombre) {
    switch (nombre) {
        case 'usuarios':   cargarUsuarios();   break;
        case 'productos':  cargarProductos();  break;
        case 'pedidos':    cargarPedidos();    break;
        case 'reservas':   cargarReservas();   break;
        case 'mesas':      cargarMesas();      break;
        case 'tematicas':  cargarTematicas();  break;
    }
}

function toast(msg, tipo = 'ok') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast' + (tipo === 'error' ? ' error' : '');
    el.classList.remove('oculta');
    setTimeout(() => el.classList.add('oculta'), 3000);
}

const ROLES_USUARIO = {
    cliente: 'Cliente',
    cajero: 'Cajero',
    administrador: 'Administrador',
};

let usuariosCache = [];

function formatearHora(fechaStr) {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr.replace(' ', 'T'));
    if (isNaN(fecha)) return fechaStr;
    const opciones = { hour: 'numeric', minute: '2-digit', hour12: true };
    return fecha.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' }) +
        ' ' + fecha.toLocaleTimeString('es-CO', opciones);
}

async function apiFetch(url, opciones = {}) {
    const resp = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        ...opciones,
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || 'Error en la petición');
    return data;
}

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

let _categorias = [];
let _categActual = null;

async function cargarProductos() {
    document.getElementById('vista-categorias').classList.remove('oculta');
    document.getElementById('vista-platos').classList.add('oculta');
    cancelarFormProducto();

    const lista = document.getElementById('lista-categorias');
    lista.innerHTML = '<div class="cargando" style="padding:20px;text-align:center;">Cargando categorías...</div>';
    try {
        _categorias = await apiFetch('/admin/api/categorias');
        if (!_categorias.length) {
            lista.innerHTML = '<div class="cargando" style="padding:20px;text-align:center;">Sin categorías</div>';
            return;
        }
        lista.innerHTML = _categorias.map(c => {
            const imgSrc = c.imagen
                ? (c.imagen.startsWith('/') || c.imagen.startsWith('http') ? c.imagen : `/static/img/${c.imagen}`)
                : null;
            const imgHtml = imgSrc
                ? `<img src="${imgSrc}" alt="" style="width:48px;height:48px;object-fit:cover;border-radius:6px;margin-right:10px;flex-shrink:0;">`
                : `<span style="width:48px;height:48px;background:rgba(255,255,255,0.08);border-radius:6px;margin-right:10px;flex-shrink:0;display:inline-block;"></span>`;
            return `
            <div class="cat-fila" style="display:flex;align-items:center;gap:0;">
                <div style="display:flex;align-items:center;flex:1;cursor:pointer;" onclick="abrirCategoria(${c.id}, '${esc(c.nombre)}')">
                    ${imgHtml}
                    <span class="cat-fila-nombre">${esc(c.nombre)}</span>
                </div>
                <button class="btn-accion azul" style="margin-right:8px;" onclick="editarCategoria(${c.id})">Editar</button>
                <span class="cat-fila-arrow" onclick="abrirCategoria(${c.id}, '${esc(c.nombre)}')" style="cursor:pointer;">&#8250;</span>
            </div>`;
        }).join('');
    } catch (e) {
        lista.innerHTML = `<div class="cargando" style="padding:20px;text-align:center;">${esc(e.message)}</div>`;
        toast(e.message, 'error');
    }
}

function abrirModalCategoria() {
    document.getElementById('form-categoria').reset();
    document.getElementById('fc-id').value = '';
    document.getElementById('fc-imagen').value = '';
    document.getElementById('fc-imagen-preview-label').textContent = '';
    document.getElementById('modal-categoria-titulo').textContent = 'Nueva Categoría';
    document.getElementById('modal-categoria').classList.remove('oculta');
    document.getElementById('fc-nombre').focus();
}
function cerrarModalCategoria() {
    document.getElementById('modal-categoria').classList.add('oculta');
}

function abrirModalProducto() {
    document.getElementById('form-producto').reset();
    document.getElementById('fp-id').value = '';
    document.getElementById('fp-imagen').value = '';
    document.getElementById('fp-imagen-preview-label').textContent = '';
    document.getElementById('modal-producto-titulo').textContent = 'Nuevo Producto';
    llenarSelectCategorias();
    if (_categActual) {
        document.getElementById('fp-categoria').value = _categActual.id;
        document.getElementById('fp-categoria-grupo').style.display = 'none';
    } else {
        document.getElementById('fp-categoria-grupo').style.display = '';
    }
    const esAdic = _categActual && _categActual.nombre.toLowerCase() === 'adiciones';
    document.getElementById('fp-stock-grupo').style.display = esAdic ? '' : 'none';
    document.getElementById('modal-producto').classList.remove('oculta');
    document.getElementById('fp-nombre').focus();
}
function cerrarModalProducto() {
    document.getElementById('modal-producto').classList.add('oculta');
}

function _cerrarModalPorOverlay(e, id) {
    if (e.target === document.getElementById(id)) {
        document.getElementById(id).classList.add('oculta');
    }
}

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        cerrarModalUsuario();
        cerrarModalCategoria();
        cerrarModalProducto();
        cerrarModalMesa();
    }
});

function cancelarFormProducto() { cerrarModalProducto(); }

async function editarCategoria(id) {
    const cat = _categorias.find(c => c.id === id);
    if (!cat) return;
    document.getElementById('fc-id').value = cat.id;
    document.getElementById('fc-nombre').value = cat.nombre;
    document.getElementById('fc-imagen').value = cat.imagen || '';
    document.getElementById('fc-imagen-file').value = '';
    const label = document.getElementById('fc-imagen-preview-label');
    if (cat.imagen) {
        const imgSrc = cat.imagen.startsWith('/') || cat.imagen.startsWith('http')
            ? cat.imagen : `/static/img/${cat.imagen}`;
        label.innerHTML = `Imagen actual: <a href="${imgSrc}" target="_blank" style="color:rgba(255,255,255,0.7)">${cat.imagen.split('/').pop()}</a>`;
    } else {
        label.textContent = '';
    }
    document.getElementById('modal-categoria-titulo').textContent = 'Editar Categoría';
    document.getElementById('modal-categoria').classList.remove('oculta');
    document.getElementById('fc-nombre').focus();
}

async function guardarCategoria(e) {
    e.preventDefault();
    const fileInput = document.getElementById('fc-imagen-file');
    if (fileInput.files.length > 0) {
        const fd = new FormData();
        fd.append('imagen', fileInput.files[0]);
        try {
            const resp = await fetch('/admin/api/upload-imagen', { method: 'POST', body: fd });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || 'Error al subir imagen');
            document.getElementById('fc-imagen').value = data.url;
        } catch (err) {
            toast(err.message, 'error');
            return;
        }
    }
    const payload = {
        nombre_categoria: document.getElementById('fc-nombre').value.trim(),
        imagen_categoria: document.getElementById('fc-imagen').value.trim() || null,
    };
    const id = document.getElementById('fc-id').value;
    try {
        if (id) {
            await apiFetch(`/admin/api/categorias/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
            toast('Categoría actualizada');
        } else {
            await apiFetch('/admin/api/categorias', { method: 'POST', body: JSON.stringify(payload) });
            toast('Categoría creada');
        }
        cerrarModalCategoria();
        cargarProductos();
    } catch (err) {
        toast(err.message, 'error');
    }
}

async function abrirCategoria(catId, catNombre) {
    _categActual = { id: catId, nombre: catNombre };
    document.getElementById('titulo-categoria').textContent = catNombre;
    document.getElementById('vista-categorias').classList.add('oculta');
    document.getElementById('vista-platos').classList.remove('oculta');
    cancelarFormProducto();

    const esAdic = catNombre.toLowerCase() === 'adiciones';
    document.getElementById('th-stock').style.display = esAdic ? '' : 'none';

    llenarSelectCategorias();
    await cargarProductosDeCategoria(catId);
}

function volverCategorias() {
    _categActual = null;
    document.getElementById('vista-platos').classList.add('oculta');
    document.getElementById('vista-categorias').classList.remove('oculta');
    cancelarFormProducto();
}

async function cargarProductosDeCategoria(catId) {
    const tbody = document.getElementById('tbody-productos');
    tbody.innerHTML = '<tr><td colspan="6" class="cargando">Cargando...</td></tr>';
    try {
        const todos = await apiFetch('/admin/api/productos');

        const filtrados = todos.filter(p => {
            const cat = _categorias.find(c => c.id === catId);
            if (!cat) return false;
            return Number(p.categoria_id) === Number(catId) || p.nombre_categoria === cat.nombre;
        });
        if (!filtrados.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="cargando">Sin productos en esta categoría</td></tr>';
            return;
        }
        tbody.innerHTML = filtrados.map(p => {
            const esAdic = _categActual && _categActual.nombre.toLowerCase() === 'adiciones';
            return `
            <tr>
                <td>${p.producto_id}</td>
                <td>${esc(p.nombre_producto)}</td>
                <td>$${Number(p.precio_base).toLocaleString('es-CO')}</td>
                ${esAdic ? `<td>${p.stock ?? 0}</td>` : ''}
                <td>
                    <span class="pill ${p.disponibilidad_producto ? 'verde' : 'rojo'}">
                        ${p.disponibilidad_producto ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td style="display:flex;gap:8px;flex-wrap:wrap;">
                    <button class="btn-accion azul" onclick="editarProducto(${p.producto_id})">Editar</button>
                    <button class="btn-accion ${p.disponibilidad_producto ? 'gris' : 'verde'}"
                        onclick="toggleProducto(${p.producto_id}, ${p.disponibilidad_producto})">
                        ${p.disponibilidad_producto ? 'Desactivar' : 'Activar'}
                    </button>
                </td>
            </tr>
        `;
        }).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function llenarSelectCategorias() {
    const sel = document.getElementById('fp-categoria');
    if (!sel) return;
    sel.innerHTML = '<option value="">-- Selecciona --</option>' +
        _categorias.map(c => `<option value="${c.id}"${_categActual && _categActual.id === c.id ? ' selected' : ''}>${esc(c.nombre)}</option>`).join('');
}

function toggleFormProducto() { abrirModalProducto(); }

function cancelarFormProducto() {
    const wrapper = document.getElementById('form-producto-wrapper');
    if (!wrapper) return;
    wrapper.classList.add('oculta');
    document.getElementById('form-producto').reset();
    document.getElementById('fp-id').value = '';
    document.getElementById('fp-imagen').value = '';
    document.getElementById('fp-imagen-preview-label').textContent = '';
    document.getElementById('form-producto-titulo').textContent = 'Nuevo Producto';
}

async function editarProducto(id) {
    try {
        const tbody = document.getElementById('tbody-productos');

        const rows = tbody.querySelectorAll('tr');

        const resp = await fetch(`/api/plato/${id}`);
        if (!resp.ok) throw new Error('No se pudo obtener el producto');
        const p = await resp.json();

        document.getElementById('fp-id').value = p.id;
        document.getElementById('fp-nombre').value = p.nombre || '';
        document.getElementById('fp-precio').value = p.precio || 0;
        document.getElementById('fp-descripcion').value = p.descripcion || '';
        document.getElementById('fp-imagen').value = p.imagen || '';

        const label = document.getElementById('fp-imagen-preview-label');
        if (p.imagen) {
            const imgUrl = p.imagen.startsWith('/') || p.imagen.startsWith('http')
                ? p.imagen
                : `/static/img/${p.imagen}`;
            label.innerHTML = `Imagen actual: <a href="${imgUrl}" target="_blank" style="color:rgba(255,255,255,0.7)">${p.imagen.split('/').pop()}</a>`;
        } else {
            label.textContent = '';
        }
        document.getElementById('fp-imagen-file').value = '';

        document.getElementById('fp-stock').value = p.stock ?? 0;
        const esAdic = _categActual && _categActual.nombre.toLowerCase() === 'adiciones';
        document.getElementById('fp-stock-grupo').style.display = esAdic ? '' : 'none';

        llenarSelectCategorias();
        const sel = document.getElementById('fp-categoria');
        sel.value = p.categoria_id || '';
        if (_categActual) {
            sel.value = _categActual.id;
            document.getElementById('fp-categoria-grupo').style.display = 'none';
        }

        document.getElementById('modal-producto-titulo').textContent = 'Editar Producto';
        document.getElementById('modal-producto').classList.remove('oculta');
        document.getElementById('fp-nombre').focus();
    } catch (e) {
        toast(e.message, 'error');
    }
}

async function guardarProducto(e) {
    e.preventDefault();
    const id = document.getElementById('fp-id').value;
    const categoriaId = Number.parseInt(document.getElementById('fp-categoria').value, 10);

    if (!Number.isInteger(categoriaId)) {
        toast('Selecciona una categoría válida', 'error');
        return;
    }

    const fileInput = document.getElementById('fp-imagen-file');
    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('imagen', fileInput.files[0]);
        try {
            const resp = await fetch('/admin/api/upload-imagen', { method: 'POST', body: formData });
            const data = await resp.json();
            if (!resp.ok) throw new Error(data.error || 'Error al subir imagen');
            document.getElementById('fp-imagen').value = data.url;
        } catch (err) {
            toast(err.message, 'error');
            return;
        }
    }

    const payload = {
        nombre_producto:         document.getElementById('fp-nombre').value.trim(),
        categoria_id:            categoriaId,
        precio_base:             parseFloat(document.getElementById('fp-precio').value),
        descripcion_producto:    document.getElementById('fp-descripcion').value.trim(),
        imagen_producto:         document.getElementById('fp-imagen').value.trim() || null,
        disponibilidad_producto: parseInt(document.getElementById('fp-disponibilidad').value),
        stock:                   parseInt(document.getElementById('fp-stock').value) || 0,
    };

    try {
        if (id) {
            await apiFetch(`/admin/api/productos/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
            toast('Producto actualizado');
        } else {
            await apiFetch('/admin/api/productos', { method: 'POST', body: JSON.stringify(payload) });
            toast('Producto agregado');
        }
        cancelarFormProducto();
        if (_categActual) {
            await cargarProductosDeCategoria(_categActual.id);
        } else {
            cargarProductos();
        }
    } catch (e) {
        toast(e.message, 'error');
    }
}

async function toggleProducto(id, estadoActual) {
    const nuevo = estadoActual ? 0 : 1;
    try {
        await apiFetch(`/admin/api/productos/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ disponibilidad_producto: nuevo }),
        });
        toast(nuevo ? 'Producto activado' : 'Producto desactivado');
        if (_categActual) {
            await cargarProductosDeCategoria(_categActual.id);
        } else {
            cargarProductos();
        }
    } catch (e) {
        toast(e.message, 'error');
    }
}

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

function esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
