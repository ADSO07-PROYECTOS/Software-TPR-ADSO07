// Bloquear fechas pasadas en el campo fecha
document.getElementById('input_fecha').min = new Date().toISOString().split('T')[0];

// Horas disponibles del restaurante (11 AM – 10 PM)
const HORAS_DISPONIBLES = [11,12,13,14,15,16,17,18,19,20,21,22];

function a12h(h) {
    const sufijo = h < 12 ? 'AM' : 'PM';
    const hora12 = h % 12 === 0 ? 12 : h % 12;
    return `${hora12}:00 ${sufijo}`;
}

// Inicializar display con hora actual de la reserva
(function init() {
    const val = document.getElementById('hora_valor').value;
    if (val !== '') {
        document.getElementById('hora_display').textContent = a12h(parseInt(val));
    }
})();

function abrirModalHora() {
    const grid = document.getElementById('horas_grid');
    grid.innerHTML = '';

    const fechaInput = document.querySelector('input[name="fecha"]').value;
    const hoy = new Date();
    const hoySolo = `${hoy.getFullYear()}-${String(hoy.getMonth()+1).padStart(2,'0')}-${String(hoy.getDate()).padStart(2,'0')}`;
    const esHoy = fechaInput === hoySolo;
    const horaActual = hoy.getHours();
    const horaSeleccionada = parseInt(document.getElementById('hora_valor').value);

    HORAS_DISPONIBLES.forEach(h => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = a12h(h);
        btn.className = 'chip_hora';

        const bloqueada = esHoy && h <= horaActual;
        if (bloqueada) {
            btn.classList.add('chip_bloqueada');
            btn.disabled = true;
        } else {
            if (h === horaSeleccionada) btn.classList.add('chip_activa');
            btn.addEventListener('click', () => seleccionarHora(h));
        }
        grid.appendChild(btn);
    });

    document.getElementById('modal_hora').classList.remove('oculto_hora');
}

function seleccionarHora(h) {
    document.getElementById('hora_valor').value = h;
    document.getElementById('hora_display').textContent = a12h(h);
    cerrarModalHora();
}

function cerrarModalHora() {
    document.getElementById('modal_hora').classList.add('oculto_hora');
}

// Cerrar al tocar fuera del cuadro
document.addEventListener('click', function(e) {
    const overlay = document.getElementById('modal_hora');
    if (e.target === overlay) cerrarModalHora();
});
