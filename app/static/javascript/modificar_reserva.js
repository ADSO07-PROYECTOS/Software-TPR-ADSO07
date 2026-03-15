document.getElementById('input_fecha').min = new Date().toISOString().split('T')[0];

const HORAS_DISPONIBLES = [11,12,13,14,15,16,17,18,19,20,21,22];

function a12h(h) {
    const sufijo = h < 12 ? 'AM' : 'PM';
    const hora12 = h % 12 === 0 ? 12 : h % 12;
    return `${hora12}:00 ${sufijo}`;
}

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

    // Si la fecha es hoy, no permitir modificar la reserva
    if (esHoy) {
        alert('No puedes modificar la reserva el día de hoy.');
        document.querySelector('input[name="fecha"]').value = '';
        document.getElementById('modal_hora').classList.add('oculto_hora');
        return;
    }

    HORAS_DISPONIBLES.forEach(h => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = a12h(h);
        btn.className = 'chip_hora';

        // Bloquear horas pasadas para cualquier fecha
        let bloqueada = false;
        if (!fechaInput) bloqueada = true;
        else {
            const fechaSeleccionada = new Date(fechaInput);
            if (fechaSeleccionada < hoy) bloqueada = true;
        }
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
// Abrir el modal de hora automáticamente al cambiar la fecha
document.querySelector('input[name="fecha"]').addEventListener('change', function() {
    abrirModalHora();
});
}

function seleccionarHora(h) {
    document.getElementById('hora_valor').value = h;
    document.getElementById('hora_display').textContent = a12h(h);
    cerrarModalHora();
}

function cerrarModalHora() {
    document.getElementById('modal_hora').classList.add('oculto_hora');
}

document.addEventListener('click', function(e) {
    const overlay = document.getElementById('modal_hora');
    if (e.target === overlay) cerrarModalHora();
});
