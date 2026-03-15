// Establecer mínimo de fecha a mañana
const inputFecha = document.getElementById('input_fecha');
const hoy = new Date();
hoy.setHours(0,0,0,0);
const manana = new Date(hoy);
manana.setDate(hoy.getDate() + 1);
inputFecha.min = manana.toISOString().split('T')[0];

const HORAS_DISPONIBLES = [11,12,13,14,15,16,17,18,19,20,21,22];

function a12h(h) {
    const sufijo = h < 12 ? 'AM' : 'PM';
    const hora12 = h % 12 === 0 ? 12 : h % 12;
    return `${hora12}:00 ${sufijo}`;
}

window.addEventListener('DOMContentLoaded', function() {
    const val = document.getElementById('hora_valor').value;
    if (val !== '') {
        document.getElementById('hora_display').textContent = a12h(parseInt(val));
    }
    window.abrirModalHora = abrirModalHora;
});

function abrirModalHora() {
    const grid = document.getElementById('horas_grid');
    grid.innerHTML = '';

    console.log('abrirModalHora ejecutada');
    const horaSeleccionada = parseInt(document.getElementById('hora_valor').value);
    HORAS_DISPONIBLES.forEach(h => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = a12h(h);
        btn.className = 'chip_hora';
        if (h === horaSeleccionada) btn.classList.add('chip_activa');
        btn.addEventListener('click', () => seleccionarHora(h));
        grid.appendChild(btn);
    });
    console.log('Botones de hora agregados:', grid.children.length);
    document.getElementById('modal_hora').classList.remove('oculto_hora');
}

// Abrir el modal de hora automáticamente al cambiar la fecha
document.querySelector('input[name="fecha"]').addEventListener('change', function() {
    abrirModalHora();
});


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
