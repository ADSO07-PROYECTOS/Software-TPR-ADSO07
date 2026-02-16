const pantalla = document.getElementById('pantalla-dinamica');
let datosUsuario = { cliente: {}, tipo: '', pedido: [] };

function render(templateId) {
    const tpl = document.getElementById(templateId);
    const clon = tpl.content.cloneNode(true);
    pantalla.innerHTML = ''; 
    pantalla.appendChild(clon);
}

function mostrarInicio() {
    datosUsuario = { cliente: {}, tipo: '', pedido: [] };
    render('tpl-inicio');
}

function seleccionarServicio(tipo) {
    datosUsuario.tipo = tipo;
    mostrarPaso1();
}

function mostrarPaso1() {
    render('tpl-paso1');
    const form = document.getElementById('form-paso1');
    
    if(datosUsuario.cliente.nom) {
        form.nom.value = datosUsuario.cliente.nom;
        form.doc.value = datosUsuario.cliente.doc;
        form.correo.value = datosUsuario.cliente.correo;
        form.tel.value = datosUsuario.cliente.tel;
    }

    form.onsubmit = (e) => {
        e.preventDefault();
        datosUsuario.cliente = Object.fromEntries(new FormData(form));
        if (datosUsuario.tipo === 'reserva') {
            mostrarDetalles();
        } else {
            mostrarPaso2();
        }
    };
}

function mostrarDetalles() {
    render('tpl-detalles');
    const contenedor = document.getElementById('contenedor-platos');
    
    const platos = [
        { id: 13, nombre: 'Pizza Mediana', precio: 32000 },
        { id: 14, nombre: 'Pizza Extragrande', precio: 58000 }
    ];

    platos.forEach(plato => {
        const div = document.createElement('div');
        div.className = 'tarjeta-plato';
        if (datosUsuario.pedido.some(p => p.id === plato.id)) div.classList.add('seleccionado');

        div.innerHTML = `<h3>${plato.nombre}</h3><p>$${plato.precio}</p>`;
        div.onclick = () => {
            div.classList.toggle('seleccionado');
            const idx = datosUsuario.pedido.findIndex(p => p.id === plato.id);
            if (idx > -1) datosUsuario.pedido.splice(idx, 1);
            else datosUsuario.pedido.push({ ...plato, cantidad: 1 });
        };
        contenedor.appendChild(div);
    });
}

async function mostrarPaso2() {
    render(datosUsuario.tipo === 'reserva' ? 'tpl-reserva' : 'tpl-domicilio');
    
    if (datosUsuario.tipo === 'reserva') {
        document.getElementById('v_fec').min = new Date().toISOString().split('T')[0];
        inyectarHoras();
        await inyectarTematicas();
    }

    const formFinal = document.getElementById('form-final');
    formFinal.onsubmit = (e) => {
        e.preventDefault();
        const datosForm = Object.fromEntries(new FormData(formFinal));
        if (datosUsuario.tipo === 'reserva') {
            const combo = document.getElementById('v_hor');
            datosForm.hor_label = combo.options[combo.selectedIndex].text;
        }
        procesarFinal(datosForm);
    };
}


function inyectarHoras() {
    const select = document.getElementById('v_hor');
    if (!select) return; 
    const apertura = 17, cierre = 25, duracion = 90; 
    let html = "";
    
    for (let min = apertura * 60; min + duracion <= cierre * 60; min += duracion) {
        const h = Math.floor(min / 60) % 24;
        const h_fin = Math.floor((min + duracion) / 60) % 24;
        
        const ampm = h >= 12 ? 'PM' : 'AM';
        const h12 = h % 12 || 12;
        
        const label = `${h12}:00 ${ampm}`;
        const valor24 = `${h.toString().padStart(2, '0')}:00`;
        
        html += `<option value="${valor24}">${label}</option>`;
    }
    select.innerHTML = html;
}

async function inyectarTematicas() {
    const select = document.getElementById('v_tematica');
    if (!select) return;

    try {
        const res = await fetch('http://localhost:5000/api/tematicas');
        const data = await res.json();
        
        if (data.length > 0) {
            select.innerHTML = data.map(t => 
                `<option value="${t.tematica_id}">${t.nombre_tematica} (+$${t.valor_tematica})</option>`
            ).join('');
        } else {
            throw new Error("Sin datos");
        }
    } catch (e) {
        select.innerHTML = `
            <option value="6">Ninguna</option>
            <option value="4">Cumpleaños</option>
            <option value="5">Aniversario</option>
        `;
    }
}
async function procesarFinal(datosForm) {
    const btn = document.getElementById('btn-submit');
    btn.disabled = true;
    btn.innerText = "PROCESANDO...";

    const payload = { 
        cliente: datosUsuario.cliente, 
        tipo: datosUsuario.tipo,
        pedido: datosUsuario.pedido,
        reserva: datosUsuario.tipo === 'reserva' ? datosForm : null,
        direccion: datosUsuario.tipo === 'domicilio' ? datosForm.direccion : null
    };

    try {
        const port = datosUsuario.tipo === 'reserva' ? '5000' : '5001';
        const res = await fetch(`http://localhost:${port}/api/${datosUsuario.tipo}s`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.status === 'success') {
            render('tpl-exito');
            document.getElementById('qr-img').src = `data:image/png;base64,${data.qr}`;
        } else { alert(data.msg); btn.disabled = false; }
    } catch (e) { alert("Error de conexión"); btn.disabled = false; }
}



mostrarInicio();

document.addEventListener('DOMContentLoaded', mostrarInicio);