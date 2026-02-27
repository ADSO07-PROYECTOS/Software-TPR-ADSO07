import{prepararPaso1, prepararPaso2, mostrarResultadoFinal, cargarTematicas, inicio} from './reservas/reservas.js';
import{seleccionarServicio, enviarAlMicroservicio} from './menu.js';


document.addEventListener('DOMContentLoaded', () => {
    const btnReservar = document.getElementById('reservar-btn');
    const btnDomicilio = document.getElementById('domicilio-btn');
    const btnVolverMenu = document.getElementById('btn_irmenu');
    const btnAtras = document.getElementById('btn_atras');

     if (btnAtras) {
        btnAtras.addEventListener('click', () => seleccionarServicio('reserva'));
    }

    if (btnVolverMenu) {
        btnVolverMenu.addEventListener('click', () => inicio());
    }

    if (btnReservar) {
        btnReservar.addEventListener('click', () => seleccionarServicio('reserva'));
    }
    
    if (btnDomicilio) {
        btnDomicilio.addEventListener('click', () => seleccionarServicio('domicilio'));
    }

    router(); 
});

const router = () => {
    const path = window.location.pathname;

    const rutas = {
        'datos_cliente': () => prepararPaso1(),
        'detalles_reserva': () => {
            cargarTematicas();
            prepararPaso2();
        },
        'exito': () => mostrarResultadoFinal()
    };

    Object.keys(rutas).forEach(route => {
        if (path.includes(route)) {
            rutas[route]();
        }
    });
};

    