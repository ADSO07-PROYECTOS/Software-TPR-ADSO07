document.addEventListener('DOMContentLoaded', () => {
    // 1. Referencias a los elementos del DOM
    const inputFoto = document.getElementById('input_foto');
    const btnEnviar = document.getElementById('enviar');
    const nombreDisplay = document.getElementById('nombre_archivo');

    // 2. Lógica para mostrar el nombre del archivo al seleccionarlo
    inputFoto.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            nombreDisplay.innerText = "Archivo: " + this.files[0].name;
        } else {
            nombreDisplay.innerText = "";
        }
    });

    // 3. Lógica para enviar el formulario
    btnEnviar.addEventListener('click', () => {
        const file = inputFoto.files[0]; // Usamos la variable correcta

        if (!file) {
            alert("Por favor, selecciona un archivo.");
            return;
        }

        // Validación de tamaño (Máximo 2MB)
        if (file.size > 2 * 1024 * 1024) {
            alert("El archivo es muy pesado. Máximo 2MB.");
            return;
        }

        // Preparar los datos
        const formData = new FormData();
        formData.append('comprobante', file);

        // Envío al servidor
        // Nota para Camilo: Asegúrate de que esta URL sea la correcta en tu backend
        fetch('/tu-endpoint-de-subida', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            console.log("Subida exitosa", data);
            alert("¡Comprobante enviado con éxito!");
        })
        .catch(err => {
            console.error("Error:", err);
            alert("Hubo un error al subir el archivo.");
        });
    });
});