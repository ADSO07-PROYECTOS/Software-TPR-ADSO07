/* ── Sidebar toggle ── */

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
