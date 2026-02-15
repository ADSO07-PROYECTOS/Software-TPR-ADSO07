document.addEventListener('DOMContentLoaded', () => {
            const detalleDiv = document.getElementById('detalle-pedido');
            const data = localStorage.getItem('pedido_cliente');

            if (data) {
                const pedido = JSON.parse(data);
                
                let html = `
                    <p><strong>Producto:</strong> ${pedido.producto}</p>
                    <p><strong>Cantidad:</strong> ${pedido.cantidad}</p>
                    <p><strong>Tamaño:</strong> ${pedido.tamano.toUpperCase()}</p>
                `;

                if (pedido.sabores && pedido.sabores.length > 0) {
                    html += <p><strong>Sabores:</strong> ${pedido.sabores.join(', ')}</p>;
                }

                if (pedido.adicionales && pedido.adicionales.length > 0) {
                    html += <p><strong>Adicionales:</strong> ${pedido.adicionales.join(', ')}</p>;
                }

                html += <div class="precio-final">Total: ${pedido.precio}</div>;
                
                detalleDiv.innerHTML = html;
            } else {
                detalleDiv.innerHTML = "<p>No hay pedido seleccionado.</p>";
            }
        });