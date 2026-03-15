document.addEventListener('DOMContentLoaded', () => {
    // 1. Referencias a los elementos del DOM
    const inputFoto = document.getElementById('input_foto');
    const btnEnviar = document.getElementById('enviar');
    const nombreDisplay = document.getElementById('nombre_archivo');
    const labelCaja = document.querySelector('.caja-subida');

    // Evitar doble apertura del diálogo
    let abriendoDialogo = false;
    labelCaja.addEventListener('click', (e) => {
        if (!abriendoDialogo) {
            abriendoDialogo = true;
            inputFoto.click();
            setTimeout(() => abriendoDialogo = false, 500);
        }
    });

    inputFoto.addEventListener('change', function() {
        if (this.files && this.files.length > 0) {
            nombreDisplay.innerText = "Archivo: " + this.files[0].name;
        } else {
            nombreDisplay.innerText = "";
        }
    });

    // 3. Lógica para enviar el formulario
    btnEnviar.addEventListener('click', async () => {
        const file = inputFoto.files[0];
        if (!file) {
            alert("Por favor, selecciona un archivo.");
            return;
        }
        // Validación de tamaño (Máximo 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert("El archivo es muy pesado. Máximo 10MB.");
            return;
        }
        // Obtener id de reserva (puedes ajustar esto según tu lógica)
        let reservaId = localStorage.getItem('id_reserva') || prompt('ID de reserva:');
        if (!reservaId) {
            alert('No se encontró el ID de la reserva.');
            return;
        }
        const formData = new FormData();
        formData.append('archivo', file);
        formData.append('reserva_id', reservaId);
        try {
            const res = await fetch('/api/reservas/comprobante', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();
            if (res.ok && data.success) {
                alert('¡Comprobante enviado con éxito!');
                // Puedes cerrar el modal aquí si tienes lógica para eso
            } else {
                alert('Error: ' + (data.message || 'No se pudo enviar el comprobante'));
            }
        } catch (err) {
            alert('Hubo un error al subir el archivo.');
            console.error("Error:", err);
        }
    });
});