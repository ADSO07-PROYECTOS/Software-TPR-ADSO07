from flask import Flask, render_template
from conexion import conectar
import requests 

app = Flask(__name__)

@app.route('/')
def inicio():
    return "El servidor principal funciona"

@app.route('/menu')
def ver_menu():
    # EN LUGAR DE CONECTAR A LA BASE DE DATOS AQUÍ...
    # ...Llamamos al microservicio (al panadero)
    
    try:
        # Hacemos una petición al otro programa que corre en el puerto 5001
        respuesta = requests.get('http://localhost:5001/api/categorias')
        
        # Convertimos la respuesta de texto a una lista de Python
        mis_categorias = respuesta.json()
        
    except:
        mis_categorias = [] # Si el microservicio está apagado, lista vacía

    # Le pasamos los datos al HTML igual que antes
    return render_template('client/menu.html', lista_categorias=mis_categorias)

if __name__ == "__main__":
    print("--- Iniciando APP PRINCIPAL en puerto 5000 ---")
    app.run(debug=True, port=5000)