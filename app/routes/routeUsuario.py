from flask import Blueprint, request, render_template, session
from models.modelsUsuario import mi_usuario

appbp = Blueprint('appbp', __name__)  # Crea el Blueprint

@appbp.route("/")
def index():
    return render_template("auth/login.html")

@appbp.route("/login", methods=['POST'])
def login():
    nUsuario = request.form.get('usuario')
    cc_usuario = request.form.get('palabra_clave')
    consulta = mi_usuario.login(cc_usuario, nUsuario)
    if not consulta:
        return render_template("auth/login.html", msg="Usuario o clave incorrectos")
    if isinstance(consulta, (tuple, list)):
        resultado, rol = consulta
    else:
        resultado = consulta
        rol = resultado.get('rol')
    if resultado.get('estado') != '1':
        return render_template("auth/login.html", msg="Usuario inactivo")
    session['id_usuario'] = resultado.get('cc_usuario')
    session['rol'] = rol
    if rol == '1':
        return render_template("auth/principal.html")
    if rol == '2':
        return render_template("admin/panel.html")
    return render_template("auth/login.html", msg="Usuario o clave incorrectos")