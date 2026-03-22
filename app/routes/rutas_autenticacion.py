"""
Blueprint – Rutas de autenticación (login / logout).
"""
from flask import Blueprint, render_template, request, redirect, session
from models.modelo_usuario import buscar_usuario_por_credenciales

bp_autenticacion = Blueprint('autenticacion', __name__)


@bp_autenticacion.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_input = request.form.get('usuario', '').strip()
        contrasena = request.form.get('palabra_clave', '').strip()

        if not nombre_input or not contrasena:
            return render_template('auth/login.html', error='Completa todos los campos')

        try:
            usuario_db = buscar_usuario_por_credenciales(nombre_input, contrasena)
        except Exception as error:
            return render_template('auth/login.html', error=f'Error de conexión: {error}')

        if not usuario_db:
            return render_template('auth/login.html',
                                   error='Credenciales incorrectas o sin acceso al panel')

        session['usuario_id'] = usuario_db['usuario_id']
        session['usuario_nombre'] = usuario_db['nombre']
        session['rol'] = usuario_db['rol']
        return redirect('/admin')

    return render_template('auth/login.html', error=None)


@bp_autenticacion.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
