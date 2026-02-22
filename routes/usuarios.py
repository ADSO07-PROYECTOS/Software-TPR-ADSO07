from conexion import *
from models.usuarios import mi_usuarios 
@app.route("/login", methods=["POST"])
def login():
    id = request.form['nom']
    contrasena = request.form['contra']
    seguir = mi_usuarios.login (id,contrasena)
    if seguir:
        session["logueado"]=True
        session["id"]= id 
        return redirect ("panel.html")
    else:
        return render_template("index.html", mensaje="Usuario o contraseña incorrectos")