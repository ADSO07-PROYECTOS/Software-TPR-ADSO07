import {
    prepararPaso1Reserva,
    prepararPaso2,
    mostrarResultadoFinal,
    cargarTematicas,
    inicio,
    abrirModalHoraReserva,
    cerrarModalHoraReserva,
} from './reservas/reservas.js';
import { seleccionarServicio } from './menu.js';
import { prepararPaso1Domicilio, prepararPasoDomicilio } from './domicilios/domicilios.js';

document.addEventListener('DOMContentLoaded', () => {
    const btnReservar = docProument.getElementById('reservar-btn');
    const btnDomicilio = document.getElementById('domicilio-btn');
    const btnVolverMenu = document.getElementById('btn_irmenu');
    const btnDescargarQR = document.getElementById('btn_descargar_qr');
    const overlay = document.getElementById('modal_hora_reserva');
           
    if (btnVolverMenu) btnVolverMenu.addEventListener('click', () => inicio());
    if (btnReservar) btnReservar.addEventListener('click', () => seleccionarServicio('reserva'));
    if (btnDomicilio) btnDomicilio.addEventListener('click', () => seleccionarServicio('domicilio'));
    if (btnDescargarQR) btnDescargarQR.addEventListener('click', descargarQR);
    window.abrirModalHoraReserva = abrirModalHoraReserva;
    window.cerrarModalHoraReserva = cerrarModalHoraReserva;
    if (overlay) {overlay.addEventListener('click', (e) => {
            if (e.target === overlay) cerrarModalHoraReserva();
        });
    }

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
        // Mensaje según tipo de servicio
        const tipo = localStorage.getItem('tipo_servicio');
        const idOrden = localStorage.getItem('id_orden') || localStorage.getItem('id_reserva') || '';
        const msgEl = document.getElementById('mensaje-exito');
        if (msgEl) {
            if (tipo === 'domicilio') {
                msgEl.textContent = `Pedido #${idOrden} registrado. \u00a1Te lo llevamos pronto!`;
            } else {
                msgEl.textContent = `Reserva #${idOrden} confirmada. \u00a1Hasta pronto!`;
            }
        }
    }

    
};

// Función para descargar el código QR
function descargarQR() {
    const qrImg = document.getElementById('qr-img');
    const idReserva = localStorage.getItem('id_reserva') || 'QR_Reserva';
    
    if (!qrImg || !qrImg.src) {
        alert('No hay código QR disponible para descargar');
        return;
    }

    // Crear un link temporal
    const link = document.createElement('a');
    link.href = qrImg.src; // El src es un data URL en base64
    link.download = `QR_Reserva_${idReserva}.png`; // Nombre del archivo a descargar
    link.style.display = 'none';
    
    // Agregar al DOM, hacer click y removoer
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

    