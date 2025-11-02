from flask import Blueprint, request, render_template, session
from models.modelsUsuario import mi_usuario

appbp = Blueprint('appbp', __name__)  # Crea el Blueprint

@appbp.route("/")
def index():
    return render_template("auth/login.html")

@appbp.route("/login", methods=['POST'])
def login():
    contrasena = request.form.get('usuario')
    cc_usuario = request.form.get('palabra_clave')
    try:
        consulta = mi_usuario.login(cc_usuario, contrasena)
    except Exception as e:
        return render_template("auth/login.html", msg="Error en el servidor, intente más tarde.")
    if consulta:
        session['id_usuario'] = consulta.get('cc_usuario') if isinstance(consulta, dict) else consulta[0]
        return render_template("admin/panel.html")
    else:
        return render_template("auth/login.html", msg="Usuario o clave incorrectos")
