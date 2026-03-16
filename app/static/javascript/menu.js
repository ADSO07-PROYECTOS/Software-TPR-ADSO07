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
    const carrito = JSON.parse(localStorage.getItem('carrito') || '[]');
    if (carrito.length === 0) {
        alert('Agrega platos al carrito primero.');
        return;
    }
    const carritoTpr = carrito.map(item => ({
        id: item.id,
        nombre: item.producto,
        cantidad: item.cantidad,
        precio: item.precio_unitario || item.precio,
        tamano: item.tamano || '',
        adicionales: item.adicionales || [],
        sabores: item.sabores || []
    }));
    localStorage.setItem('carrito_tpr', JSON.stringify(carritoTpr));
    localStorage.setItem('tipo_servicio', tipo);
    window.location.href = '/datos_cliente';
}

export async function enviarAlMicroservicio() {
    alert('Usa el flujo de reserva o domicilio desde el carrito.');
}