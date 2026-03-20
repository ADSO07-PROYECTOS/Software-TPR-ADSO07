/* ── CRUD de Productos y Categorías ── */

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

async function editarProducto(id) {
    try {
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
