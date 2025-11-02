from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from conexion import *
from models.modelsUsuario import mi_usuario

app = Flask(__name__)
app.secret_key = "replace-with-a-secure-random-key"
app.permanent_session_lifetime = timedelta(minutes=30)

#Importacion de la funcion crear_conexion desde conexion.py
crear_conexion()

# Ruta principal
@app.route("/")
def index():
    return render_template("auth/login.html")

# Rutas de autenticación
@app.route("/login", methods=["POST"])
def login():
    cc_usuario = request.form.get("cc_usuario", "")
    contrasena = request.form.get("contrasena", "")
    
    print(f"[APP] Recibido: cc_usuario='{cc_usuario}', contrasena='{contrasena}'")
    
    usuario_data = mi_usuario.login(cc_usuario, contrasena)

    if usuario_data:
        print(f"[APP] Login exitoso para: {usuario_data}")
        session['cc_usuario'] = usuario_data['cc_usuario']
        session['rol'] = usuario_data['rol']
        return render_template("admin/panel.html")
    else:
        print(f"[APP] Login fallido")
        return render_template("auth/login.html", error="Credenciales inválidas. Inténtalo de nuevo.")
    
    


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)