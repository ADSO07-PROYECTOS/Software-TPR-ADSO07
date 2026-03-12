from flask import Flask, render_template, request, redirect
from conexion import conectar
import requests 

app = Flask(__name__)

MENU_SERVICE_URL = 'http://localhost:5001'

#-- Ruta Principal --

@app.route('/')
def inicio():
    return render_template('client/inicio.html')

# -- Ruta del microservicio de menu --

@app.route('/menu')
def ver_menu():
    try:
        respuesta = requests.get(f'{MENU_SERVICE_URL}/api/categorias', timeout=10)
        respuesta.raise_for_status()
        mis_categorias = respuesta.json()
        print(f"Categorías recibidas: {mis_categorias}")
        
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        mis_categorias = [] 
 
    return render_template('client/menu.html', lista_categorias=mis_categorias)

#-- Ruta de ver el detalle de los platos

@app.route('/menu/<int:id_categoria>')
def ver_platos(id_categoria):
    mis_platos = []
    lista_categorias = []
    nombre_categoria = "Platos"

    try:
        # Obtener todos los platos de la categoría seleccionada
        url_platos = f'{MENU_SERVICE_URL}/api/platos/{id_categoria}'
        respuesta_platos = requests.get(url_platos, timeout=10)
        respuesta_platos.raise_for_status()
        mis_platos = respuesta_platos.json()
        print(f"Platos recibidos para categoría {id_categoria}: {mis_platos}")

        # Obtener todas las categorías para mostrar el selector
        respuesta_cats = requests.get(f'{MENU_SERVICE_URL}/api/categorias', timeout=10)
        respuesta_cats.raise_for_status()
        lista_categorias = respuesta_cats.json()

        # Buscar el nombre de la categoría actual
        nombre_categoria = next(
            (cat['nombre'] for cat in lista_categorias if cat['id'] == id_categoria),
            "Platos"
        )

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con microservicio: {e}")
    except Exception as e:
        print(f"Error general: {e}")

    return render_template(
        'client/ver_platos.html',
        lista_platos=mis_platos,
        lista_categorias=lista_categorias,
        id_categoria_actual=id_categoria,
        nombre_categoria=nombre_categoria
    )



@app.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    datos_extras = {"tamanos": [], "adiciones": [], "sabores": []} # Valores por defecto

    try:
        # 1. Pedir info del plato
        url_plato = f'{MENU_SERVICE_URL}/api/plato/{id_plato}'
        res_plato = requests.get(url_plato, timeout=5)
        
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        # 2. Pedir info de extras (Tamaños, adiciones, sabores)
        url_extras = f'{MENU_SERVICE_URL}/api/extras'
        res_extras = requests.get(url_extras, timeout=5)

        if res_extras.status_code == 200:
            datos_extras = res_extras.json()

    except Exception as e:
        print(f"Error conectando microservicios: {e}")

    
    return render_template('client/detalle_plato.html', 
                           plato=info_plato,
                           tamanos=datos_extras.get('tamanos', []),
                           adiciones=datos_extras.get('adiciones', []),
                           sabores=datos_extras.get('sabores', []))


@app.route('/resumen_pedido')
def resumen_pedido():
    return render_template('client/resumen_pedido.html')



@app.route('/hacer_reserva', methods=['GET', 'POST'])
def hacer_reserva():
    if request.method == 'POST':
        try:
            # Recopilar datos del formulario
            datos_cliente = {
                "nom": request.form['nombre'],
                "correo": request.form['email']
            }
            datos_reserva = {
                "fec": request.form['fecha'],
                "hor": request.form['hora']
            }
            
            # Estructura de datos para el microservicio
            payload = {
                "cliente": datos_cliente,
                "reserva": datos_reserva
            }

            # Llamada al microservicio de reservas
            url_microservicio = 'http://localhost:5005/api/reservas'
            respuesta = requests.post(url_microservicio, json=payload, timeout=10)
            respuesta.raise_for_status()
            
            # Si todo va bien, redirigir a una página de éxito o inicio
            return redirect('/')

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con el microservicio de reservas: {e}")
            # Aquí podrías renderizar una página de error
            return "Error al procesar la reserva.", 500
        except Exception as e:
            print(f"Error general: {e}")
            return "Ocurrió un error inesperado.", 500

    # Si es GET, simplemente muestra el formulario
    return render_template('client/reserva_base.html')

@app.route('/reserva/<int:id_reserva>')
def ver_reserva(id_reserva):
    try:
        url_microservicio = f'http://localhost:5005/reserva/{id_reserva}'
        respuesta = requests.get(url_microservicio, timeout=10)
        respuesta.raise_for_status()
        
        datos_reserva = respuesta.json()
        print(f"Datos de reserva recibidos: {datos_reserva}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con microservicio de reserva: {e}")
        datos_reserva = {"status": "error", "msg": "Error al obtener los datos de la reserva"}

    return render_template('client/detalle_reserva_qr.html', reserva=datos_reserva)



if __name__ == "__main__":
    try:
        print("--- Iniciando APP PRINCIPAL en puerto 5000 ---")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"ERROR AL INICIAR EL SERVIDOR: {e}")
