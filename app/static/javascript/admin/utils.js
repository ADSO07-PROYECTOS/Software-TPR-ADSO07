/* ── Utilidades compartidas del panel admin ── */

function esc(str) {
    if (str === null || str === undefined) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function toast(msg, tipo = 'ok') {
    const el = document.getElementById('toast');
    el.textContent = msg;
    el.className = 'toast' + (tipo === 'error' ? ' error' : '');
    el.classList.remove('oculta');
    setTimeout(() => el.classList.add('oculta'), 3000);
}

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
