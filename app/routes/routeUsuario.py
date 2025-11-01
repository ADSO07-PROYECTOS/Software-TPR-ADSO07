from flask import request, render_template, session
from conexion import *
from models.modelsUsuario import mi_usuario

app = crear_app()

@app.route("/login", methods=['POST'])
def login():
    cc_usuario = request.form.get('usuario')
    contrasena = request.form.get('palabra_clave')
    try:
        consulta = mi_usuario.login(cc_usuario, contrasena)
    except Exception as e:
            # loguear e y retornar mensaje amigable
        return render_template("auth/login.html", msg="Error en el servidor, intente más tarde.")
    if consulta:
            # consulta viene como dict (cursor dictionary=True)
        session['id_usuario'] = consulta.get('cc_usuario') if isinstance(consulta, dict) else consulta[0]
        return render_template("auth/registro.html")
    else:
        return render_template("auth/login.html", msg="Usuario o clave incorrectos") 