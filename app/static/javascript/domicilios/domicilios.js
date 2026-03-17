const API_DOMICILIOS = '/api/domicilios';

export function prepararPaso1Domicilio() {
    const form = document.getElementById('form-paso1');
    if (!form) return;

    form.onsubmit = (e) => {
        e.preventDefault();
        const cliente = {
            nom: form.nom.value,
            doc: form.doc.value,
            correo: form.correo.value,
            tel: form.tel.value
        };
        localStorage.setItem('cliente_temporal', JSON.stringify(cliente));

        window.location.href = '/direccion_domicilio'; 
    };
}

export function prepararPasoDomicilio() {
    const form = document.getElementById('form-domicilio');
    if (!form) return;

    form.onsubmit = async (e) => {
        e.preventDefault();
        const btn = document.getElementById('btn-submit-dom');
        btn.disabled = true;
        btn.innerText = "PROCESANDO..."; // Le damos feedback visual al usuario

        // 1. VALIDACIÓN DE SEGURIDAD: Verificar que los datos del cliente aún existan
        let clienteTemporal = null;
        try {
            clienteTemporal = JSON.parse(localStorage.getItem('cliente_temporal') || 'null');
        } catch (_e) {
            clienteTemporal = null;
        }

        if (!clienteTemporal || !clienteTemporal.doc || !clienteTemporal.nom) {
            alert('No se encontraron los datos del cliente. Vuelve al paso anterior e inténtalo de nuevo.');
            btn.disabled = false;
            btn.innerText = 'ENVIAR PEDIDO'; // Ajusta este texto al que tenga tu botón
            return;
        }

        const payload = {
            cliente: clienteTemporal,
            domicilio: {
                direccion: form.direccion.value + ', ' + form.referencia.value,
                metodo_pago: form.metodo_pago.value
            },
            productos: JSON.parse(localStorage.getItem('carrito_tpr')) || []
        };

        try {
            const res = await fetch(API_DOMICILIOS, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                localStorage.setItem('qr_reserva', data.qr); // El exito.html usa esta variable para la imagen
                localStorage.setItem('id_orden', data.id);

                // 2. TÁCTICA DE SEGURIDAD: Borramos el cliente temporal además del carrito
                localStorage.removeItem('cliente_temporal');
                localStorage.removeItem('carrito');
                localStorage.removeItem('carrito_tpr');

                // 3. TÁCTICA DE HISTORIAL: Usamos replace() en lugar de href
                if (payload.domicilio.metodo_pago === 'transferencia') {
                    localStorage.setItem('id_domicilio', data.id);
                    const total = payload.productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0);
                    localStorage.setItem('total_domicilio', total);
                    window.location.replace('/subir_comprobante_domicilio');
                } else {
                    window.location.replace('/exito');
                }
            } else {
                alert("Error: " + data.message);
                btn.disabled = false;
                btn.innerText = 'ENVIAR PEDIDO';
            }
        } catch (error) {
            alert("Error al conectar con el servicio de domicilios");
            btn.disabled = false;
            btn.innerText = 'ENVIAR PEDIDO';
        }
    };
}

export function mostrarResultadoFinal() {
    const img = document.getElementById('qr-img');
    const qrData = localStorage.getItem('qr_reserva');
    if (img && qrData) img.src = `data:image/png;base64,${qrData}`;
}

