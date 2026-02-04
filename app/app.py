from flask import Flask, render_template
from conexion import conectar
from app.models.modelos import Categoria


app = Flask(__name__)


@app.route('/')
def inicio():
    return "El servidor esta funcionando!"

@app.route('/menu')
def ver_menu():
    mis_categorias = Categoria.obtener_todas()

    return render_template('client/menu.html', lista_categorias=mis_categorias)


if __name__ == "__main__":
    print("--- Iniciando Verificacion de Base de Datos ---")
    app.run(debug=True, host="0.0.0.0", port=5000)
    miconexion = conectar()
    
    
    
    
