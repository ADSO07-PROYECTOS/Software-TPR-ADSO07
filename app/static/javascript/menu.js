document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.querySelector('.menu-btn');
  const menu = document.querySelector('.menu-desplegable-cont');

  if (!menuBtn || !menu) return;

  menuBtn.addEventListener('click', (e) => {
    e.stopPropagation(); 
    menu.classList.toggle('activo');
  });

  menu.addEventListener('click', (e) => {
    e.stopPropagation();
  });

  document.addEventListener('click', () => {
    menu.classList.remove('activo');
  });
});

export function seleccionarServicio(tipo) {
       /*  const carrito = JSON.parse(localStorage.getItem('carrito_tpr')) || JSON.parse(localStorage.getItem('carrito_seleccionado')) || [];
        if (!carrito || carrito.length === 0) return alert("Selecciona platos primero");
 */
        localStorage.setItem('tipo_servicio', tipo);
       /*  localStorage.setItem('carrito_tpr', JSON.stringify(carrito)); */
        window.location.href = '/datos_cliente';
    }

    // Enviar los datos guardados en localStorage al microservicio correspondiente
export async function enviarAlMicroservicio() {
    const carrito = JSON.parse(localStorage.getItem('carrito_tpr')) || JSON.parse(localStorage.getItem('carrito_seleccionado')) || [];
        if (!carrito || carrito.length === 0) return alert('Selecciona platos primero');

        const tipo = localStorage.getItem('tipo_servicio') || 'reserva';
        const cliente = JSON.parse(localStorage.getItem('cliente')) || JSON.parse(localStorage.getItem('cliente_tpr')) || {};
        const detalles = JSON.parse(localStorage.getItem('detalles_servicio')) || {};

        const url = tipo === 'reserva'
            ? 'http://localhost:5000/api/reservas'
            : 'http://localhost:5001/api/domicilios';

        const payload = tipo === 'reserva'
            ? { cliente: cliente, reserva: detalles, pedido: carrito }
            : { cliente: cliente, direccion: detalles.direccion || detalles.direccion_text || '', pedido: carrito };

        try {
            const res = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();

            if (data.status === 'success') {
                localStorage.setItem('resultado_qr', data.qr || '');
                localStorage.setItem('resultado_msg', tipo === 'reserva' ? `Reserva #${data.id} confirmada` : `Pedido #${data.id} en camino`);
                window.location.href = '/exito';
            } else {
                alert('Error: ' + (data.message || 'Respuesta inesperada del servidor'));
            }
        } catch (e) {
            alert('Error de conexión con el microservicio (revisa que esté corriendo en localhost)');
        }
}