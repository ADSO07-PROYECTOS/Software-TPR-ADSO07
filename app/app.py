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

if __name__ == "__main__":
    print("--- Iniciando APP PRINCIPAL en puerto 5000 ---")
    app.run(debug=True, port=5000)