from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from conexion import conectar
import requests 

app = Flask(__name__)
CORS(app)


@app.route('/')
def inicio():
    return ver_menu()

@app.route('/menu')
def ver_menu():
    try:
        respuesta = requests.get('http://localhost:5001/api/categorias', timeout=10)
        respuesta.raise_for_status()
        mis_categorias = respuesta.json()
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        mis_categorias = [] 
    return render_template('client/menu.html', lista_categorias=mis_categorias)

@app.route('/datos_cliente')
def vista_cliente():
    return render_template('client/detalles_cliente.html')

@app.route('/direccion_domicilio')
def vista_domicilio():
    return render_template('client/direccion_domicilio.html')
    
@app.route('/detalles_reserva')
def vista_reserva():
    lista_tematicas = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
            lista_tematicas = cursor.fetchall()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error al obtener temáticas: {e}")

    return render_template('client/detalles_reserva.html', tematicas=lista_tematicas)

@app.route('/exito')
def vista_exito():
    return render_template('client/exito.html')

@app.route('/resumen/reserva/<int:id_reserva>')
def resumen_reserva(id_reserva):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT r.*, t.nombre_tematica
            FROM reservas r
            LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
            WHERE r.reserva_id = %s
        """, (id_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return "Reserva no encontrada", 404

        cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (reserva['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("""
            SELECT dr.cantidad, dr.valor_unitario, p.nombre_producto
            FROM detalles_reservas dr
            JOIN productos p ON dr.producto_id = p.producto_id
            WHERE dr.reserva_id = %s
        """, (id_reserva,))
        productos = cursor.fetchall()

        cursor.close(); conn.close()
        return render_template('client/resumen_reserva.html',
                               reserva=reserva,
                               cliente=cliente,
                               productos=productos,
                               tematica=reserva.get('nombre_tematica', 'N/A'))
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/resumen/domicilio/<int:id_domicilio>')
def resumen_domicilio(id_domicilio):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM domicilios WHERE domicilio_id = %s", (id_domicilio,))
        domicilio = cursor.fetchone()
        if not domicilio:
            return "Domicilio no encontrado", 404

        cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (domicilio['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("""
            SELECT dd.cantidad, dd.valor_unitario, p.nombre_producto
            FROM detalles_domicilios dd
            JOIN productos p ON dd.producto_id = p.producto_id
            WHERE dd.domicilio_id = %s
        """, (id_domicilio,))
        productos = cursor.fetchall()

        cursor.close(); conn.close()
        return render_template('client/resumen_domicilio.html',
                               domicilio=domicilio,
                               cliente=cliente,
                               productos=productos)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/carrito')
def ver_carrito():
    return render_template('client/carrito.html')


@app.route('/menu/<int:id_categoria>')
def ver_platos(id_categoria):
    mis_platos = []
    try:
        url_microservicio = f'http://localhost:5001/api/platos/{id_categoria}'
        respuesta = requests.get(url_microservicio, timeout=10)
        respuesta.raise_for_status()
        mis_platos = respuesta.json()
    except Exception as e:
        print(f"Error al obtener platos: {e}")
    return render_template('client/ver_platos.html', lista_platos=mis_platos)

@app.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    datos_extras = {"tamanos": [], "adiciones": [], "sabores": []}
    try:
        res_plato = requests.get(f'http://localhost:5001/api/plato/{id_plato}', timeout=5)
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        res_extras = requests.get('http://localhost:5001/api/extras', timeout=5)
        if res_extras.status_code == 200:
            datos_extras = res_extras.json()
    except Exception as e:
        print(f"Error en detalle plato: {e}")

    categoria_nombre = info_plato.get('categoria_nombre', '').lower()
    es_pizza = 'pizza' in categoria_nombre

    return render_template('client/detalle_plato.html', 
                           plato=info_plato,
                           es_pizza=es_pizza,
                           tamanos=datos_extras.get('tamanos', []),
                           adiciones=datos_extras.get('adiciones', []),
                           sabores=datos_extras.get('sabores', []))

@app.route('/api/tematicas', methods=['GET'])
def proxy_tematicas():
    try:
        resp = requests.get('http://127.0.0.1:5005/api/tematicas', timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/reservas', methods=['POST'])
def proxy_reservas():
    try:
        resp = requests.post('http://127.0.0.1:5005/api/reservas',
                             json=request.json, timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)