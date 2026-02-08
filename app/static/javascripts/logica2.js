const pantalla = document.getElementById('pantalla-dinamica');

export class prueba {

    componentes = {

    };
        
    navegar(vista) { pantalla.innerHTML = componentes[vista]; }

    irAPaso2() {
    const cliente = { 
        nom: document.getElementById('v_nom').value, 
        correo: document.getElementById('v_mail').value,
        doc: document.getElementById('v_doc').value 
    };
    if(!cliente.nom || !cliente.correo.includes('@')) return alert("Ingresa un correo válido");
    localStorage.setItem('temp_cliente', JSON.stringify(cliente));
    navegar('paso2');
    }

    irAPaso3() {

        const reserva = { 
            fec: document.getElementById('v_fec').value, 
            hor: document.getElementById('v_hor').value,
            // cant: document.getElementById('v_cant').value,
            // piso: document.getElementById('v_piso').value,
        };
    
        if(!reserva.fec || !reserva.hor) return alert("Completa fecha y hora");
        localStorage.setItem('temp_reserva', JSON.stringify(reserva));
        navegar('paso3');
        const cli = JSON.parse(localStorage.getItem('temp_cliente'));
        document.getElementById('caja-resumen').innerHTML = `<p><b>Para:</b> ${cli.nom}</p><p><b>Día:</b> ${reserva.fec} - ${reserva.hor}</p>`;
    }

    async enviarBackend() {
    const body = { cliente: JSON.parse(localStorage.getItem('temp_cliente')), reserva: JSON.parse(localStorage.getItem('temp_reserva')) };
        try {
            const res = await fetch('http://localhost:5000/api/reservas', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            navegar('final');
            const img = document.getElementById('qr-resultado');
            img.src = `data:image/png;base64,${data.qr}`;
            document.getElementById('btn-descarga').onclick = () => {
                const link = document.createElement('a');
                link.href = img.src; link.download = "Mi_Reserva.png"; link.click();
            };
            } catch (e) { alert("Error al conectar con el servidor"); }
        }
        

}

    
   document.addEventListener('DOMContentLoaded', () => navegar('paso1' ));

    
