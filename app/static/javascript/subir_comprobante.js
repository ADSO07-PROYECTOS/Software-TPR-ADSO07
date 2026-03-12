// Manejador para subir comprobante de transferencia

document.addEventListener('DOMContentLoaded', () => {
    const inputFile = document.getElementById('input_foto');
    const labelCaja = document.querySelector('.caja-subida');
    const nombreArchivo = document.getElementById('nombre_archivo');
    const btnEnviar = document.getElementById('enviar');
    const totalPagar = document.getElementById('total-pagar');

    let archivoSeleccionado = null;

    // Obtener ID de reserva desde localStorage
    const idReserva = localStorage.getItem('id_reserva');
    if (!idReserva) {
        alert('Error: No se encontró el ID de la reserva');
        window.location.href = '/menu';
        return;
    }

    // Simular click al label para abrir file picker
    labelCaja.addEventListener('click', () => {
        inputFile.click();
    });

    // Cuando se selecciona un archivo
    inputFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            // Validar tipo
            const esImagen = file.type.startsWith('image/');
            const esPDF = file.type === 'application/pdf';
            
            if (!esImagen && !esPDF) {
                alert('Por favor, selecciona una imagen o PDF');
                inputFile.value = '';
                nombreArchivo.textContent = '';
                archivoSeleccionado = null;
                return;
            }

            // Validar tamaño (máximo 10MB)
            if (file.size > 10 * 1024 * 1024) {
                alert('El archivo es muy grande. Máximo 10MB.');
                inputFile.value = '';
                nombreArchivo.textContent = '';
                archivoSeleccionado = null;
                return;
            }

            archivoSeleccionado = file;
            nombreArchivo.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
            nombreArchivo.style.color = '#38761d';
        }
    });

    // Enviar comprobante
    btnEnviar.addEventListener('click', async () => {
        if (!archivoSeleccionado) {
            alert('Por favor, selecciona un comprobante');
            return;
        }

        btnEnviar.disabled = true;
        btnEnviar.textContent = 'ENVIANDO...';

        const formData = new FormData();
        formData.append('archivo', archivoSeleccionado);
        formData.append('reserva_id', idReserva);

        try {
            console.log('Enviando comprobante para reserva:', idReserva);
            const res = await fetch('/api/reservas/comprobante', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            console.log('Respuesta:', data);

            if (res.ok && data.success) {
                alert('✓ Comprobante enviado correctamente. Tu reserva está en revisión.');
                window.location.href = '/exito';
            } else {
                const errorMsg = data.message || 'No se pudo enviar el comprobante';
                console.error('Error:', errorMsg);
                alert('Error: ' + errorMsg);
                btnEnviar.disabled = false;
                btnEnviar.textContent = 'ENVIAR COMPROBANTE';
            }
        } catch (error) {
            console.error('Error de conexión:', error);
            alert('Error de conexión: ' + error.message);
            btnEnviar.disabled = false;
            btnEnviar.textContent = 'ENVIAR COMPROBANTE';
        }
    });
});
