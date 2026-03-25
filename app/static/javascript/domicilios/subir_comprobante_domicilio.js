document.addEventListener('DOMContentLoaded', () => {
    const inputFile    = document.getElementById('input_foto');
    const labelCaja    = document.querySelector('.caja-subida');
    const nombreArchivo = document.getElementById('nombre_archivo');
    const btnEnviar    = document.getElementById('enviar');
    const totalPagar   = document.getElementById('total-pagar');

    let archivoSeleccionado = null;

    const idDomicilio = localStorage.getItem('id_domicilio');
    if (!idDomicilio) {
        alert('Error: No se encontró el ID del domicilio');
        window.location.href = '/menu';
        return;
    }

    const totalGuardado = localStorage.getItem('total_domicilio');
    if (totalPagar && totalGuardado) {
        totalPagar.textContent = `$ ${Number(totalGuardado).toLocaleString('es-CO')}`;
    }

    inputFile.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const tiposPermitidos = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf'];
        const extPermitidas = ['png', 'jpg', 'jpeg', 'pdf'];
        const ext = file.name.split('.').pop().toLowerCase();

        if (!tiposPermitidos.includes(file.type) && !extPermitidas.includes(ext)) {
            alert('Formato no permitido. Solo se aceptan archivos PNG, JPG o PDF.');
            inputFile.value = '';
            nombreArchivo.textContent = '';
            archivoSeleccionado = null;
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            alert('El archivo es muy grande. Máximo 5MB.');
            inputFile.value = '';
            nombreArchivo.textContent = '';
            archivoSeleccionado = null;
            return;
        }

        archivoSeleccionado = file;
        nombreArchivo.textContent = `📄 ${file.name} (${(file.size / 1024).toFixed(2)} KB)`;
        nombreArchivo.style.color = '#38761d';
    });

    btnEnviar.addEventListener('click', async () => {
        if (!archivoSeleccionado) {
            alert('Por favor, selecciona un comprobante');
            return;
        }

        btnEnviar.disabled = true;
        btnEnviar.textContent = 'ENVIANDO...';

        const formData = new FormData();
        formData.append('archivo', archivoSeleccionado);
        formData.append('domicilio_id', idDomicilio);

        try {
            const res  = await fetch('/api/domicilios/comprobante', {
                method: 'POST',
                body: formData
            });
            const data = await res.json();

            if (res.ok && data.success) {
                alert('✓ Comprobante enviado correctamente. Tu domicilio está en revisión.');
                localStorage.removeItem('id_domicilio');
                localStorage.removeItem('total_domicilio');
                window.location.href = '/exito';
            } else {
                alert('Error: ' + (data.message || 'No se pudo enviar el comprobante'));
                btnEnviar.disabled = false;
                btnEnviar.textContent = 'ENVIAR COMPROBANTE';
            }
        } catch (error) {
            alert('Error de conexión: ' + error.message);
            btnEnviar.disabled = false;
            btnEnviar.textContent = 'ENVIAR COMPROBANTE';
        }
    });
});
