import { prepararPaso1Reserva, prepararPaso2, mostrarResultadoFinal, cargarTematicas, inicio } from './reservas/reservas.js';
import { seleccionarServicio } from './menu.js';
import { prepararPaso1Domicilio, prepararPasoDomicilio } from './domicilios/domicilios.js';

document.addEventListener('DOMContentLoaded', () => {
    const btnReservar = document.getElementById('reservar-btn');
    const btnDomicilio = document.getElementById('domicilio-btn');
    const btnVolverMenu = document.getElementById('btn_irmenu');

    if (btnVolverMenu) btnVolverMenu.addEventListener('click', () => inicio());
    if (btnReservar) btnReservar.addEventListener('click', () => seleccionarServicio('reserva'));
    if (btnDomicilio) btnDomicilio.addEventListener('click', () => seleccionarServicio('domicilio'));

    router(); 
});

function establecerFechaMinima() {
    const inputFecha = document.getElementById('v_fec');
    const hoy = new Date().toISOString().split('T')[0];
    inputFecha.min = hoy;
}

const router = () => {
    const path = window.location.pathname;
    const tipoServicio = localStorage.getItem('tipo_servicio');

    if (path.includes('datos_cliente')) {
        if (tipoServicio === 'domicilio') {
            prepararPaso1Domicilio();
        } else {
            prepararPaso1Reserva();
        }
    } 
    else if (path.includes('detalles_reserva')) {
        cargarTematicas();
        prepararPaso2();
        establecerFechaMinima();
    } 
    else if (path.includes('direccion_domicilio')) {
        prepararPasoDomicilio();
    }
    else if (path.includes('exito')) {
        mostrarResultadoFinal();
    }

    
};

    