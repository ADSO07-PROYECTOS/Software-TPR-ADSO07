let accionActual = ""; 
let idReservaSeleccionada = null;

function obtenerElementos() {
    return {
        modal: document.getElementById('cubrir_modal'),
        titulo: document.getElementById('ttlo_modal'),
        desc: document.getElementById('descripcion_modal'),
        btnConfirmar: document.getElementById('modal_confirmar'),
        btnCancelar: document.getElementById('modal_eliminar')
    };
}

function abrirModal(type, id) {
    const el = obtenerElementos();
    accionActual = type;
    idReservaSeleccionada = id;
    
    if (type === 'EDITAR') {
        el.titulo.innerText = "MODIFICACIÓN DE RESERVA";
        el.titulo.style.color = "#99181F";
        el.desc.innerText = `¿Deseas modificar los datos de la reserva #${id}?`;
    } else if (type === 'ELIMINAR') {
        el.titulo.innerText = "CANCELACIÓN DE RESERVA";
        el.titulo.style.color = "#99181F"; 
        el.desc.innerText = `¿Estás seguro de eliminar la reserva #${id}? Esta acción no se puede deshacer.`;
    }

    el.modal.classList.remove('oculto');
}

document.addEventListener('DOMContentLoaded', () => {
    const el = obtenerElementos();

    el.btnConfirmar.addEventListener('click', () => {
        if (accionActual === 'EDITAR') {
            window.location.href = `modificar_reserva.html?id=${idReservaSeleccionada}`;
        } else if (accionActual === 'BORRAR') {
            ejecutarEliminacion(idReservaSeleccionada);
        }
    });

    el.btnCancelar.addEventListener('click', () => {
        el.modal.classList.add('oculto');
    });
});

async function ejecutarEliminacion(id) {
    try {
        const respuesta = await fetch('/eliminar_reserva.py', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id_reserva: id })
        });
        const resultado = await respuesta.json();
        if (resultado.success) {
            alert("Reserva eliminada.");
            location.reload(); 
        } else {
            alert("Error: " + resultado.message);
        }
    } catch (e) {
        console.error("Error:", e);
    }
}