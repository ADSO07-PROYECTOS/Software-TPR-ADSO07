import {
    prepararPaso1Reserva,
    prepararPaso2,
    mostrarResultadoFinal,
    cargarTematicas,
    inicio,
    abrirModalHoraReserva,
    cerrarModalHoraReserva,
    hora
} from './reservas/reservas.js';
import { seleccionarServicio } from './menu.js';
import { prepararPaso1Domicilio, prepararPasoDomicilio } from './domicilios/domicilios.js';

document.addEventListener('DOMContentLoaded', () => {
    const btnReservar = document.getElementById('reservar-btn');
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
    
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) cerrarModalHoraReserva();
        });
    }

    router(); 
});

function establecerFechaMinima() {
    const inputFecha = document.getElementById('v_fec');
    if (!inputFecha) return;

    const fechaMinima = new Date();
    fechaMinima.setDate(fechaMinima.getDate() + 1); 
    
    const minDateStr = fechaMinima.toISOString().split('T')[0];
    
    inputFecha.min = minDateStr;
    inputFecha.value = minDateStr;
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
        establecerFechaMinima(); 
        prepararPaso2();
    } 
    else if (path.includes('direccion_domicilio')) {
        prepararPasoDomicilio();
    }
    else if (path.includes('exito')) {
        mostrarResultadoFinal();
        const tipo = localStorage.getItem('tipo_servicio');
        const idOrden = localStorage.getItem('id_orden') || localStorage.getItem('id_reserva') || '';
        const msgEl = document.getElementById('mensaje-exito');
        if (msgEl) {
            if (tipo === 'domicilio') {
                msgEl.textContent = `Pedido #${idOrden} registrado. ¡Te lo llevamos pronto!`;
            } else {
                msgEl.textContent = `Reserva #${idOrden} confirmada. ¡Hasta pronto!`;
            }
        }
    }
};

function descargarQR() {
    const qrImg = document.getElementById('qr-img');
    const idReserva = localStorage.getItem('id_reserva') || 'QR_Reserva';
    
    if (!qrImg || !qrImg.src) {
        alert('No hay código QR disponible para descargar');
        return;
    }

    const link = document.createElement('a');
    link.href = qrImg.src; 
    link.download = `QR_Reserva_${idReserva}.png`; 
    link.style.display = 'none';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}