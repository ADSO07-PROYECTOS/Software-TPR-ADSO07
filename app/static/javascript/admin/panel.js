/* ═══════════════════════════════════════════════════════
   PANEL ADMINISTRACIÓN – TRES PASOS
   ═══════════════════════════════════════════════════════ */

// ── Sidebar responsive (hamburguesa) ─────────────────────────────────────────

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

// ── Navegación entre secciones ────────────────────────────────────────────────

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const target = btn.dataset.section;
        // Activar botón
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Mostrar sección
        document.querySelectorAll('.seccion').forEach(s => s.classList.remove('activa'));
        document.getElementById('sec-' + target).classList.add('activa');
        // En móvil cerrar sidebar al navegar
        if (window.innerWidth <= 900) {
            document.getElementById('panel_izq').classList.remove('abierto');
            document.getElementById('sidebar-overlay').classList.remove('visible');
        }
        // Cargar datos de la sección (excepto dashboard que viene del servidor)
        if (target !== 'dashboard') cargarSeccion(target);
    });
});

function cargarSeccion(nombre) {
    switch (nombre) {
        case 'usuarios':   cargarUsuarios();   break;
        case 'productos':  cargarProductos();  break;
        case 'pedidos':    cargarPedidos();    break;
        case 'reservas':   cargarReservas();   break;
        case 'tematicas':  cargarTematicas();  break;
    }
}

// ── Toast ─────────────────────────────────────────────────────────────────────

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

// ── Helper fetch JSON ─────────────────────────────────────────────────────────
// ── Formatear hora a 12h AM/PM ────────────────────────────────────────────────
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

// ══════════════════════════════════════════════════════════════════════════════
// USUARIOS
// ══════════════════════════════════════════════════════════════════════════════

async function cargarUsuarios() {
    const tbody = document.getElementById('tbody-usuarios');
    tbody.innerHTML = '<tr><td colspan="7" class="cargando">Cargando...</td></tr>';
    try {
        usuariosCache = await apiFetch('/admin/api/clientes');
        if (!usuariosCache.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="cargando">Sin usuarios registrados</td></tr>';
            return;
        }
        tbody.innerHTML = usuariosCache.map(c => `
            <tr>
                <td>${c.cliente_id}</td>
                <td>${esc(c.cc_cliente)}</td>
                <td>${esc(c.nombre)}</td>
                <td>${esc(c.email || '')}</td>
                <td>${esc(c.telefono || '')}</td>
                <td><span class="pill ${pillRol(c.rol)}">${esc(formatearRol(c.rol))}</span></td>
                <td>
                    <button class="btn-accion azul" onclick="editarUsuario(${c.cliente_id})">
                        Editar
                    </button>
                    <button class="btn-accion rojo" onclick="eliminarCliente(${c.cliente_id})">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
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
    document.getElementById('fu-rol').value = 'cliente';
    document.getElementById('modal-usuario-titulo').textContent = 'Nuevo Usuario';
    document.getElementById('modal-usuario').classList.remove('oculta');
    document.getElementById('fu-cedula').focus();
}

function cerrarModalUsuario() {
    document.getElementById('modal-usuario').classList.add('oculta');
}

function editarUsuario(id) {
    const usuario = usuariosCache.find(item => item.cliente_id === id);
    if (!usuario) {
        toast('Usuario no encontrado', 'error');
        return;
    }

    document.getElementById('fu-id').value = usuario.cliente_id;
    document.getElementById('fu-cedula').value = usuario.cc_cliente || '';
    document.getElementById('fu-nombre').value = usuario.nombre || '';
    document.getElementById('fu-email').value = usuario.email || '';
    document.getElementById('fu-telefono').value = usuario.telefono || '';
    document.getElementById('fu-rol').value = usuario.rol || 'cliente';
    document.getElementById('modal-usuario-titulo').textContent = 'Editar Usuario';
    document.getElementById('modal-usuario').classList.remove('oculta');
    document.getElementById('fu-nombre').focus();
}

async function guardarUsuario(e) {
    e.preventDefault();

    const id = document.getElementById('fu-id').value;
    const payload = {
        cc_cliente: document.getElementById('fu-cedula').value.trim(),
        nombre: document.getElementById('fu-nombre').value.trim(),
        email: document.getElementById('fu-email').value.trim(),
        telefono: document.getElementById('fu-telefono').value.trim(),
        rol: document.getElementById('fu-rol').value,
    };

    try {
        if (id) {
            await apiFetch(`/admin/api/clientes/${id}`, {
                method: 'PUT',
                body: JSON.stringify(payload),
            });
            toast('Usuario actualizado');
        } else {
            await apiFetch('/admin/api/clientes', {
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

async function eliminarCliente(id) {
    const usuario = usuariosCache.find(item => item.cliente_id === id);
    const nombre = usuario ? usuario.nombre : `#${id}`;
    if (!confirm(`¿Eliminar al cliente "${nombre}"? Esta acción no se puede deshacer.`)) return;
    try {
        await apiFetch(`/admin/api/clientes/${id}`, { method: 'DELETE' });
        toast('Cliente eliminado');
        cargarUsuarios();
    } catch (e) {
        toast(e.message, 'error');
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// PRODUCTOS – vista por categoría
// ══════════════════════════════════════════════════════════════════════════════

let _categorias = [];
let _categActual = null; // { id, nombre }

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
        lista.innerHTML = _categorias.map(c => `
            <div class="cat-fila" onclick="abrirCategoria(${c.id}, '${esc(c.nombre)}')"> 
                <span class="cat-fila-nombre">${esc(c.nombre)}</span>
                <span class="cat-fila-arrow">›</span>
            </div>`
        ).join('');
    } catch (e) {
        lista.innerHTML = `<div class="cargando" style="padding:20px;text-align:center;">${esc(e.message)}</div>`;
        toast(e.message, 'error');
    }
}

/* ── Modales ─────────────────────────────────────────── */
function abrirModalCategoria() {
    document.getElementById('form-categoria').reset();
    document.getElementById('fc-imagen').value = '';
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
    }
});

// Alias de compatibilidad (cancelarFormProducto sigue siendo llamado internamente)
function cancelarFormProducto() { cerrarModalProducto(); }

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
    try {
        await apiFetch('/admin/api/categorias', { method: 'POST', body: JSON.stringify(payload) });
        toast('Categoría creada');
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
    // preseleccionar categoría en el formulario
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
    tbody.innerHTML = '<tr><td colspan="5" class="cargando">Cargando...</td></tr>';
    try {
        const todos = await apiFetch('/admin/api/productos');
        const productos = todos.filter(p => p.nombre_categoria === (_categorias.find(c => c.id === catId) || {}).nombre
            || todos.filter(p2 => p2.nombre_categoria).length === 0
        );
        // Filtrar por categoria_id si existe el campo, si no por nombre
        const filtrados = todos.filter(p => {
            const cat = _categorias.find(c => c.id === catId);
            return cat && p.nombre_categoria === cat.nombre;
        });
        if (!filtrados.length) {
            tbody.innerHTML = '<tr><td colspan="5" class="cargando">Sin productos en esta categoría</td></tr>';
            return;
        }
        tbody.innerHTML = filtrados.map(p => `
            <tr>
                <td>${p.producto_id}</td>
                <td>${esc(p.nombre_producto)}</td>
                <td>$${Number(p.precio_base).toLocaleString('es-CO')}</td>
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
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" class="cargando">${esc(e.message)}</td></tr>`;
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
        // Buscar en la tabla actual
        const rows = tbody.querySelectorAll('tr');
        // Necesitamos traer detalles completos; lo buscamos en memoria desde la última carga
        // Hacemos re-fetch rápido del producto individual
        const resp = await fetch(`/api/plato/${id}`);
        if (!resp.ok) throw new Error('No se pudo obtener el producto');
        const p = await resp.json();

        document.getElementById('fp-id').value = p.id;
        document.getElementById('fp-nombre').value = p.nombre || '';
        document.getElementById('fp-precio').value = p.precio || 0;
        document.getElementById('fp-descripcion').value = p.descripcion || '';
        document.getElementById('fp-imagen').value = p.imagen || '';
        // Mostrar nombre del archivo actual si existe
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

    // Subir imagen si el usuario seleccionó un archivo
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
        categoria_id:            parseInt(document.getElementById('fp-categoria').value),
        precio_base:             parseFloat(document.getElementById('fp-precio').value),
        descripcion_producto:    document.getElementById('fp-descripcion').value.trim(),
        imagen_producto:         document.getElementById('fp-imagen').value.trim() || null,
        disponibilidad_producto: parseInt(document.getElementById('fp-disponibilidad').value),
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

// ══════════════════════════════════════════════════════════════════════════════
// PEDIDOS (DOMICILIOS)
// ══════════════════════════════════════════════════════════════════════════════

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
        tbody.innerHTML = domicilios.map(d => `
            <tr>
                <td>${d.domicilio_id}</td>
                <td>${esc(d.nombre || '')}<br><small>${esc(d.telefono || '')}</small></td>
                <td>${esc(d.direccion || '')}</td>
                <td>$${d.total ? Number(d.total).toLocaleString('es-CO') : '0'}</td>
                <td>${d.pago_transferencia ? '🏦 Transferencia' : '💵 Efectivo'}</td>
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
        `).join('');
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

// ══════════════════════════════════════════════════════════════════════════════
// RESERVAS
// ══════════════════════════════════════════════════════════════════════════════

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

// Abrir modal para revisar comprobante
async function abrirModalComprobante(reservaId) {
    try {
        const reservas = await apiFetch('/admin/api/reservas');
        const reserva = reservas.find(r => r.reserva_id === reservaId);
        
        if (!reserva || !reserva.comprobante_transferencia) {
            alert('Comprobante no encontrado');
            return;
        }

        const modal = document.getElementById('modal-comprobante');
        const img = document.getElementById('comprobante-preview');
        const enlace = document.getElementById('comprobante-enlace');
        const titulo = document.querySelector('#modal-comprobante .modal-header h2');
        const btnConfirmar = document.getElementById('btn-confirmar-comprobante');

        titulo.textContent = `Comprobante Reserva #${reservaId} - ${reserva.cc_cliente}`;
        
        const rutaComprobante = `/static/${reserva.comprobante_transferencia}`;
        
        // Si es PDF
        if (reserva.comprobante_transferencia.endsWith('.pdf')) {
            img.style.display = 'none';
            enlace.href = rutaComprobante;
            enlace.style.display = 'block';
            enlace.textContent = '📄 Ver PDF en nueva ventana';
        } else {
            // Si es imagen
            img.src = rutaComprobante;
            img.style.display = 'block';
            enlace.style.display = 'none';
        }

        btnConfirmar.dataset.reservaId = reservaId;
        modal.classList.remove('oculta');
    } catch (e) {
        alert('Error al abrir comprobante: ' + e.message);
    }
}

function cerrarModalComprobante() {
    document.getElementById('modal-comprobante').classList.add('oculta');
}

async function confirmarComprobante(reservaId) {
    if (!confirm('¿Confirmar este comprobante de transferencia?')) return;
    
    try {
        const btn = event.target;
        btn.disabled = true;
        btn.textContent = 'CONFIRMANDO...';

        await apiFetch(`/admin/api/reservas/${reservaId}`, {
            method: 'PUT',
            body: JSON.stringify({ 
                estado: 'confirmada',
                comprobante_validado: true
            }),
        });

        cerrarModalComprobante();
        toast(`✓ Comprobante validado. Reserva confirmada.`);
        cargarReservas(); // Recargar tabla
    } catch (e) {
        alert('Error: ' + e.message);
        event.target.disabled = false;
        event.target.textContent = '✓ CONFIRMAR PAGO';
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// TEMÁTICAS
// ══════════════════════════════════════════════════════════════════════════════

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

// ── Utilidad: escapado HTML (previene XSS) ────────────────────────────────────
function esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}
