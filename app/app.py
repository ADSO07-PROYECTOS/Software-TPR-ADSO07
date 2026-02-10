from flask import Flask, render_template, request, redirect
from conexion import conectar
import requests 

app = Flask(__name__)

#-- Ruta Principal --

@app.route('/')
def inicio():
    return "El servidor principal funciona"

# -- Ruta del microservicio de menu --

@app.route('/menu')
def ver_menu():
    try:
        respuesta = requests.get('http://localhost:5001/api/categorias', timeout=10)
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
    nombre_categoria = "Platos" # Valor por defecto
    
    try:
        url_microservicio = f'http://localhost:5001/api/platos/{id_categoria}'
        respuesta = requests.get(url_microservicio, timeout=10)
        respuesta.raise_for_status()
        
        mis_platos = respuesta.json()
        print(f"Platos recibidos para categoría {id_categoria}: {mis_platos}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con microservicio: {e}")
    except Exception as e:
        print(f"Error general: {e}")

    return render_template('client/ver_platos.html', lista_platos=mis_platos)



@app.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    datos_extras = {"tamanos": [], "adiciones": [], "sabores": []} # Valores por defecto

    try:
        # 1. Pedir info del plato
        url_plato = f'http://localhost:5001/api/plato/{id_plato}'
        res_plato = requests.get(url_plato, timeout=5)
        
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        # 2. Pedir info de extras (Tamaños, adiciones, sabores)
        url_extras = 'http://localhost:5001/api/extras'
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
    return render_template('client/v2/reserva_base.html')



if __name__ == "__main__":
    try:
        print("--- Iniciando APP PRINCIPAL en puerto 5000 ---")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"ERROR AL INICIAR EL SERVIDOR: {e}")
