/* ── Permisos por rol ── */

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
