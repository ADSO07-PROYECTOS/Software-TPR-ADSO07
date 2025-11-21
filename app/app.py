from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from conexion import conectar


app = Flask(__name__)


@app.route('/')
def inicio():
    return "El servidor esta funcionando!"


if __name__ == "__main__":
    print("--- Iniciando Verificacion de Base de Datos ---")
    app.run(debug=True, host="0.0.0.0", port=5000)
    miconexion = conectar()
    
    
    
    
