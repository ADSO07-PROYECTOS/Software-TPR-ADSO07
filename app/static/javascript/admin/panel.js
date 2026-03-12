/* ═══════════════════════════════════════════════════════
   PANEL ADMINISTRACIÓN – TRES PASOS
   ═══════════════════════════════════════════════════════ */

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

// ── Helper fetch JSON ─────────────────────────────────────────────────────────

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
    tbody.innerHTML = '<tr><td colspan="6" class="cargando">Cargando...</td></tr>';
    try {
        const clientes = await apiFetch('/admin/api/clientes');
        if (!clientes.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="cargando">Sin usuarios registrados</td></tr>';
            return;
        }
        tbody.innerHTML = clientes.map(c => `
            <tr>
                <td>${c.cliente_id}</td>
                <td>${esc(c.cc_cliente)}</td>
                <td>${esc(c.nombre)}</td>
                <td>${esc(c.email || '')}</td>
                <td>${esc(c.telefono || '')}</td>
                <td>
                    <button class="btn-accion rojo" onclick="eliminarCliente(${c.cliente_id}, '${esc(c.nombre)}')">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

async function eliminarCliente(id, nombre) {
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
// PRODUCTOS
// ══════════════════════════════════════════════════════════════════════════════

let _categorias = [];

async function cargarProductos() {
    const tbody = document.getElementById('tbody-productos');
    tbody.innerHTML = '<tr><td colspan="6" class="cargando">Cargando...</td></tr>';
    try {
        const [productos, categorias] = await Promise.all([
            apiFetch('/admin/api/productos'),
            apiFetch('/admin/api/categorias'),
        ]);
        _categorias = categorias;
        llenarSelectCategorias();

        if (!productos.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="cargando">Sin productos</td></tr>';
            return;
        }
        tbody.innerHTML = productos.map(p => `
            <tr>
                <td>${p.producto_id}</td>
                <td>${esc(p.nombre_producto)}</td>
                <td>${esc(p.nombre_categoria || '')}</td>
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
        tbody.innerHTML = `<tr><td colspan="6" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function llenarSelectCategorias() {
    const sel = document.getElementById('fp-categoria');
    sel.innerHTML = '<option value="">-- Selecciona --</option>' +
        _categorias.map(c => `<option value="${c.id}">${esc(c.nombre)}</option>`).join('');
}

function toggleFormProducto() {
    const wrapper = document.getElementById('form-producto-wrapper');
    wrapper.classList.toggle('oculta');
    if (!wrapper.classList.contains('oculta')) llenarSelectCategorias();
}

function cancelarFormProducto() {
    document.getElementById('form-producto-wrapper').classList.add('oculta');
    document.getElementById('form-producto').reset();
    document.getElementById('fp-id').value = '';
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

        llenarSelectCategorias();
        const sel = document.getElementById('fp-categoria');
        sel.value = p.categoria_id || '';

        document.getElementById('form-producto-titulo').textContent = 'Editar Producto';
        document.getElementById('form-producto-wrapper').classList.remove('oculta');
        document.getElementById('form-producto-wrapper').scrollIntoView({ behavior: 'smooth' });
    } catch (e) {
        toast(e.message, 'error');
    }
}

async function guardarProducto(e) {
    e.preventDefault();
    const id = document.getElementById('fp-id').value;
    const payload = {
        nombre_producto:       document.getElementById('fp-nombre').value.trim(),
        categoria_id:          parseInt(document.getElementById('fp-categoria').value),
        precio_base:           parseFloat(document.getElementById('fp-precio').value),
        descripcion_producto:  document.getElementById('fp-descripcion').value.trim(),
        imagen_producto:       document.getElementById('fp-imagen').value.trim() || null,
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
        cargarProductos();
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
        cargarProductos();
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
                <td><small>${esc(d.fecha_pedido || '')}</small></td>
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

const ESTADOS_RESERVA = ['confirmada', 'ocupada', 'cancelada', 'finalizada'];

async function cargarReservas() {
    const tbody = document.getElementById('tbody-reservas');
    tbody.innerHTML = '<tr><td colspan="9" class="cargando">Cargando...</td></tr>';
    try {
        const reservas = await apiFetch('/admin/api/reservas');
        if (!reservas.length) {
            tbody.innerHTML = '<tr><td colspan="9" class="cargando">Sin reservas registradas</td></tr>';
            return;
        }
        tbody.innerHTML = reservas.map(r => `
            <tr>
                <td>${r.reserva_id}</td>
                <td>${esc(r.nombre || '')}<br><small>${esc(r.telefono || '')}</small></td>
                <td><small>${esc(r.fecha_hora || '')}</small></td>
                <td>${r.cantidad_personas}</td>
                <td>${r.piso || '—'}</td>
                <td>${esc(r.nombre_tematica || '—')}</td>
                <td>${r.pago_transferencia ? '🏦 Transfer.' : '💵 Efectivo'}</td>
                <td><span class="pill ${pillRes(r.estado)}">${esc(r.estado || '')}</span></td>
                <td>
                    <select class="sel-estado" onchange="cambiarEstadoReserva(${r.reserva_id}, this.value)">
                        ${ESTADOS_RESERVA.map(s =>
                            `<option value="${s}" ${s === r.estado ? 'selected' : ''}>${s}</option>`
                        ).join('')}
                    </select>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="9" class="cargando">${esc(e.message)}</td></tr>`;
        toast(e.message, 'error');
    }
}

function pillRes(estado) {
    const mapa = {
        'confirmada': 'verde', 'ocupada': 'azul',
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

// ══════════════════════════════════════════════════════════════════════════════
// TEMÁTICAS
// ══════════════════════════════════════════════════════════════════════════════

async function cargarTematicas() {
    const tbody = document.getElementById('tbody-tematicas');
    tbody.innerHTML = '<tr><td colspan="3" class="cargando">Cargando...</td></tr>';
    try {
        const tematicas = await apiFetch('/admin/api/tematicas');
        if (!tematicas.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="cargando">Sin temáticas registradas</td></tr>';
            return;
        }
        tbody.innerHTML = tematicas.map(t => `
            <tr>
                <td>${t.tematica_id}</td>
                <td>${esc(t.nombre_tematica)}</td>
                <td>
                    <button class="btn-accion rojo"
                        onclick="eliminarTematica(${t.tematica_id}, '${esc(t.nombre_tematica)}')">
                        Eliminar
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="3" class="cargando">${esc(e.message)}</td></tr>`;
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
