/* ── Navegación entre secciones del panel ── */

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

document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        cerrarModalUsuario();
        cerrarModalCategoria();
        cerrarModalProducto();
        cerrarModalMesa();
    }
});
