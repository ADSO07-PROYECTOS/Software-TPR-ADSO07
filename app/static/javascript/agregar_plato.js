// MODIFICACIÓN EN TU JS:
document.addEventListener("DOMContentLoaded", function() {
    console.log("JS cargado y DOM listo"); 

    const btnNuevoPlato = document.getElementById('btn-nuevo-plato');

    if (btnNuevoPlato) {
        console.log("Botón encontrado"); 
        btnNuevoPlato.addEventListener('click', function() {
            cargarModal(); 
        });
    } else {
        console.error("No se encontró el botón con ID 'btn-nuevo-plato'");
    }
});
const btnNuevoPlato = document.getElementById('btn-nuevo-plato');

if (btnNuevoPlato) {
    btnNuevoPlato.addEventListener('click', function() {
        cargarModal(); 
    });
}

// 2. Función para inyectar el HTML
function cargarModal() {
    console.log("Clic detectado, intentando cargar el modal...");

    const contenedor = document.getElementById('contenedor-modal');

    if (contenedor.innerHTML.trim() !== "") {
        document.getElementById('modal-plato').style.display = 'flex';
        return;
    }

    fetch('/modal_plato.html') 
        .then(respuesta => respuesta.text()) 
        .then(html => {
            contenedor.innerHTML = html; 
            document.getElementById('modal-plato').style.display = 'flex'; 
            
            activarEnvioFormulario();
        })
        .catch(error => console.error('Error al cargar el modal:', error));
}

// 3. Función para cerrar
function cerrarModal() {
    document.getElementById('modal-plato').style.display = 'none';
}

// 4. Lógica de envío a la Base de Datos
function activarEnvioFormulario() {
    const formulario = document.getElementById('form-nuevo-plato');

    if (formulario) {
        formulario.addEventListener('submit', function(evento) {
            evento.preventDefault(); 

            let datosFormulario = new FormData();
            datosFormulario.append('nombre', document.getElementById('input-nombre').value);
            datosFormulario.append('descripcion', document.getElementById('input-desc').value);
            datosFormulario.append('precio', document.getElementById('input-precio').value);
            
            let inputFoto = document.getElementById('input-foto');
            if (inputFoto.files.length > 0) {
                datosFormulario.append('foto', inputFoto.files[0]);
            }
            //CAMILO O BEDOYA LO ACOMODAN 
            fetch('/api/guardar_plato', { 
                method: 'POST',
                body: datosFormulario 
            })
            .then(respuesta => respuesta.json()) 
            .then(datos => {
                alert("Plato guardado con éxito");
                cerrarModal(); 
                location.reload(); 
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Hubo un problema al guardar.");
            });
        });
    }
}