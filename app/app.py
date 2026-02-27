from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from conexion import conectar
import requests 

app = Flask(__name__)
CORS(app)

# -- RUTAS DE NAVEGACIÓN --

@app.route('/')
def inicio():
    return ver_menu()

@app.route('/menu')
def ver_menu():
    try:
        # El microservicio de menú está en el 5001 según tu código previo
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

@app.route('/detalles_reserva')
def vista_reserva():
    # Esta es la versión ÚNICA y correcta de la ruta
    lista_tematicas = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Consultamos la tabla 'tematica'
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
            lista_tematicas = cursor.fetchall()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error al obtener temáticas: {e}")

    # Asegúrate de que la ruta al archivo sea correcta según tu estructura
    return render_template('client/detalles_reserva.html', tematicas=lista_tematicas)

@app.route('/exito')
def vista_exito():
    return render_template('client/exito.html')

# -- RUTAS DE DATOS (PLATOS Y DETALLES) --

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
        # Consulta al microservicio de menú (puerto 5001)
        res_plato = requests.get(f'http://localhost:5001/api/plato/{id_plato}', timeout=5)
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        res_extras = requests.get('http://localhost:5001/api/extras', timeout=5)
        if res_extras.status_code == 200:
            datos_extras = res_extras.json()
    except Exception as e:
        print(f"Error en detalle plato: {e}")

    return render_template('client/detalle_plato.html', 
                           plato=info_plato,
                           tamanos=datos_extras.get('tamanos', []),
                           adiciones=datos_extras.get('adiciones', []),
                           sabores=datos_extras.get('sabores', []))

if __name__ == "__main__":
    app.run(debug=True, port=5000)