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

        const payload = {
            cliente: JSON.parse(localStorage.getItem('cliente_temporal')),
            domicilio: {
                direccion: form.direccion.value+', '+form.referencia.value,
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
                localStorage.setItem('qr_reserva', data.qr);
                localStorage.setItem('id_orden', data.id);

                localStorage.removeItem('carrito');
                localStorage.removeItem('carrito_tpr');

                if (payload.domicilio.metodo_pago === 'transferencia') {
                    localStorage.setItem('id_domicilio', data.id);
                    const total = payload.productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0);
                    localStorage.setItem('total_domicilio', total);
                    window.location.href = '/subir_comprobante_domicilio';
                } else {
                    window.location.href = '/exito';
                }
            } else {
                alert("Error: " + data.message);
                btn.disabled = false;
            }
        } catch (error) {
            alert("Error al conectar con el servicio de domicilios");
            btn.disabled = false;
        }
    };
}

export function mostrarResultadoFinal() {
    const img = document.getElementById('qr-img');
    const qrData = localStorage.getItem('qr_reserva');
    if (img && qrData) img.src = `data:image/png;base64,${qrData}`;
}