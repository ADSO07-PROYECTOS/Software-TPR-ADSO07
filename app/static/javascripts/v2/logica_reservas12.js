const pantalla = document.getElementById('pantalla-dinamica');
let datosUsuario = { cliente: {}, tipo: '' };

function mostrarInicio() {
    datosUsuario = { cliente: {}, tipo: '' }; 
    pantalla.innerHTML = `
        <header><h1>BIENVENIDO</h1></header>
        <div style="display: flex; flex-direction: column; gap: 15px;">
            <button class="btn-grande2" onclick="seleccionarServicio('reserva')">RESERVAR MESA</button>
            <button class="btn-grande" onclick="seleccionarServicio('domicilio')">PEDIR DOMICILIO</button>
        </div>
    `;
}

function seleccionarServicio(tipo) {
    datosUsuario.tipo = tipo;
    mostrarPaso1();
}

function mostrarPaso1() {
    pantalla.innerHTML = `
        <header><h1>TUS DATOS</h1></header>
        <div class="grupo-entrada">
            <label>Nombre</label>
            <input type="text" id="v_nom" value="${datosUsuario.cliente.nom || ''}">
        </div>
        <div class="grupo-entrada">
            <label>Cédula</label>
            <input type="number" id="v_doc" value="${datosUsuario.cliente.doc || ''}">
        </div>
        <div class="grupo-entrada">
            <label>Teléfono</label>
            <input type="tel" id="v_tel" value="${datosUsuario.cliente.tel || ''}">
        </div>
        <div class="grupo-entrada">
            <label>Correo</label>
            <input type="email" id="v_mail" value="${datosUsuario.cliente.correo || ''}">
        </div>
        <div style="display: flex; gap: 10px;">
            <button onclick="mostrarInicio()" id="btn-atras">VOLVER</button>
            <button onclick="validarPaso1()" class="btn-grande2">CONTINUAR</button>
        </div>
    `;
}

function validarPaso1() {
    const nom = document.getElementById('v_nom').value;
    const doc = document.getElementById('v_doc').value;
    const tel = document.getElementById('v_tel').value;
    const mail = document.getElementById('v_mail').value;

    if (!nom || !doc || !tel || !mail) return alert("Llena todos los campos");
    
    datosUsuario.cliente = { nom, doc, tel, correo: mail };
    
    if (datosUsuario.tipo === 'reserva') mostrarPasoReserva();
    else mostrarPasoDomicilio();
}

function mostrarPasoReserva() {
    pantalla.innerHTML = `
        <header><h1>DETALLES MESA</h1></header>
        <div class="grupo-entrada"><label>Fecha</label><input type="date" id="v_fec"></div>
        <div class="grupo-entrada"><label>Hora</label><input type="time" id="v_hor"></div>
        <div class="grupo-entrada">
            <label>Piso</label>
            <select id="v_piso"><option value="1">Piso 1</option><option value="2">Piso 2</option></select>
        </div>
        <div class="grupo-entrada">
            <label>Temática</label>
            <select id="v_tematica">
                <option value="1">Estándar</option>
                <option value="2">Cumpleaños</option>
                <option value="3">Aniversario</option>
            </select>
        </div>
        <div class="grupo-entrada">
            <label>Método de Pago</label>
            <select id="v_pago">
                <option value="efectivo">Efectivo (Local)</option>
                <option value="transferencia">Transferencia</option>
            </select>
        </div>
        <div class="grupo-entrada">
            <label>Observación</label>
            <input id="v_desc" placeholder="Opcional"></input>
        </div>
        
        <div style="display: flex; gap: 10px;">
            <button onclick="mostrarPaso1()" id="btn-atras">ATRÁS</button>
            <button onclick="enviarFinal('reserva')" class="btn-grande2">CONFIRMAR</button>
        </div>
    `;
}

function mostrarPasoDomicilio() {
    pantalla.innerHTML = `
        <header><h1>ENTREGA</h1></header>
        <div class="grupo-entrada">
            <label>Dirección exacta</label>
            <input type="text" id="v_dir">
        </div>
        
        <div style="display: flex; gap: 10px;">
            <button onclick="mostrarPaso1()" id="btn-atras">ATRÁS</button>
            <button onclick="enviarFinal('domicilio')" class="btn-grande2">PEDIR YA</button>
        </div>
    `;
}

async function enviarFinal(tipo) {
    let payload = { cliente: datosUsuario.cliente };
    // Usamos 127.0.0.1 explícitamente para evitar errores de resolución de DNS
    let puerto = tipo === 'reserva' ? 5005 : 5001;
    let endpoint = tipo === 'reserva' ? '/api/reservas' : '/api/domicilios';
    
    // URL Corregida: NO usar localhost
    const url = `http://127.0.0.1:${puerto}${endpoint}`;

    if (tipo === 'reserva') {
        const fec = document.getElementById('v_fec').value;
        const hor = document.getElementById('v_hor').value;
        const piso = document.getElementById('v_piso').value;
        const tematica = document.getElementById('v_tematica').value;
        const pago = document.getElementById('v_pago').value;
        const desc = document.getElementById('v_desc').value;

        if (!fec || !hor) return alert("Selecciona fecha y hora");

        payload.reserva = {
            fec: fec,
            hor: hor,
            piso: piso,
            tematica: tematica,
            metodo_pago: pago, 
            desc: desc || "Sin observaciones"
        };
    } else {
        const dir = document.getElementById('v_dir').value;
        if (!dir) return alert("Ingresa la dirección");
        payload.direccion = dir;
    }

    console.log("Enviando datos a:", url);
    console.log("Payload:", payload);

    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        console.log("Respuesta status:", res.status);
        const data = await res.json();
        console.log("Data recibida:", data);
        
        if (data.status === 'success') {
            pantalla.innerHTML = `
                <header><h1>¡LISTO!</h1></header>
                <div style="text-align: center; color: white;">
                    <p>Enviamos los detalles a <b>${datosUsuario.cliente.correo}</b></p>
                    <img id="img-qr" src="data:image/png;base64,${data.qr}" style="width: 200px; border: 5px solid white; margin: 15px 0;">
                    <br>
                    <button onclick="descargarQR()" class="btn-grande2" style="margin-bottom: 10px;">DESCARGAR QR</button>
                    <button onclick="location.reload()" id="btn-atras">VOLVER AL INICIO</button>
                </div>
            `;
        } else {
            alert("Error del servidor: " + data.msg);
        }
    } catch (e) {
        console.error("Error Fetch:", e);
        alert("Error de conexión. Asegúrate que el microservicio esté corriendo en el puerto " + puerto);
    }
}

function descargarQR() {
    const img = document.getElementById('img-qr');
    const link = document.createElement('a');
    link.href = img.src;
    link.download = "QR_TresPasos.png";
    link.click();
}

// Iniciar
mostrarInicio();