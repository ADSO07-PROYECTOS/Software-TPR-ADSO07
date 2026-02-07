from flask import Flask, render_template
from conexion import conectar
import requests 

app = Flask(__name__)

@app.route('/')
def inicio():
    return "El servidor principal funciona"

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



@app.route('/menu/<int:id_categoria>')
def ver_platos(id_categoria):
    mis_platos = []
    nombre_categoria = "Platos" # Valor por defecto
    
    try:
        # 1. Llamamos al microservicio pasándole el ID de la categoría
        url_microservicio = f'http://localhost:5001/api/platos/{id_categoria}'
        respuesta = requests.get(url_microservicio, timeout=10)
        respuesta.raise_for_status()
        
        mis_platos = respuesta.json()
        print(f"Platos recibidos para categoría {id_categoria}: {mis_platos}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con microservicio: {e}")
    except Exception as e:
        print(f"Error general: {e}")

    # Renderizamos la plantilla 'ver_platos.html' enviando la lista
    # Nota: Asegúrate de que la ruta del template sea correcta según tu estructura
    return render_template('client/ver_platos.html', lista_platos=mis_platos)


@app.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    try:
        # Llamamos al microservicio pidiendo el plato especifico
        url_microservicio = f'http://localhost:5001/api/plato/{id_plato}'
        respuesta = requests.get(url_microservicio, timeout=10)
        
        if respuesta.status_code == 200:
            info_plato = respuesta.json()
        else:
            print("Error: Plato no encontrado en microservicio")

    except Exception as e:
        print(f"Error conectando microservicio: {e}")

    # Renderizamos la plantilla (asegúrate de guardar tu HTML con este nombre)
    return render_template('client/detalle_plato.html', plato=info_plato)


if __name__ == "__main__":
    print("--- Iniciando APP PRINCIPAL en puerto 5000 ---")
    app.run(debug=True, port=5000)