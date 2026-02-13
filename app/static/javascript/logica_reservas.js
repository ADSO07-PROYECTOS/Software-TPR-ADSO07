const pantalla = document.getElementById('pantalla-dinamica');

const componentes = {
    paso1: `
        <header><h1>TUS DATOS</h1></header>
        <div class="grupo-entrada">
            <label>Nombre</label>
            <input type="text" id="v_nom">
        </div>
        <div class="grupo-entrada">
            <label>Correo Electrónico</label>
            <input type="email" id="v_mail">
        </div>
        <div class="grupo-entrada">
            <label>Identificación</label>
            <input type="text" id="v_doc"></div>
        <button onclick="irAPaso2()">CONTINUAR</button>
    `,
    paso2: `
        <header><h1>DATOS RESERVA</h1></header>
        <div class="grupo-entrada"><label>Fecha</label><input type="date" id="v_fec"></div>
        <div class="grupo-entrada"><label>Hora</label><input type="time" id="v_hor"></div>
        <button onclick="irAPaso3()">VER RESUMEN</button>
    `,
    paso3: `
        <header><h1>CONFIRMAR</h1></header>
        <div class="resumen-caja" id="caja-resumen"></div>
        <button onclick="enviarBackend()">CONFIRMAR Y RECIBIR CORREO</button>
    `,
    final: `
        <header><h1>TU CÓDIGO QR</h1></header>
        <img id="qr-resultado">
        <button id="btn-descarga">GUARDAR QR</button>
    `
};

function navegar(vista) { pantalla.innerHTML = componentes[vista]; }

function irAPaso2() {
    const cliente = { 
        nom: document.getElementById('v_nom').value, 
        correo: document.getElementById('v_mail').value,
        doc: document.getElementById('v_doc').value 
    };
    if(!cliente.nom || !cliente.correo.includes('@')) return alert("Ingresa un correo válido");
    localStorage.setItem('temp_cliente', JSON.stringify(cliente));
    navegar('paso2');
}

function irAPaso3() {
    const reserva = { fec: document.getElementById('v_fec').value, hor: document.getElementById('v_hor').value };
    if(!reserva.fec || !reserva.hor) return alert("Completa fecha y hora");
    localStorage.setItem('temp_reserva', JSON.stringify(reserva));
    navegar('paso3');
    const cli = JSON.parse(localStorage.getItem('temp_cliente'));
    document.getElementById('caja-resumen').innerHTML = `<p><b>Para:</b> ${cli.nom}</p><p><b>Día:</b> ${reserva.fec} - ${reserva.hor}</p>`;
}

async function enviarBackend() {
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

document.addEventListener('DOMContentLoaded', () => navegar('paso1'));