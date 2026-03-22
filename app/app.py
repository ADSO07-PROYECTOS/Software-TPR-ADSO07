"""
Punto de entrada principal – Sabores Unidos.
Registra los Blueprints y arranca el servidor Flask.
"""
import os
from flask import Flask
from flask_cors import CORS

try:
    from flask_debugtoolbar import DebugToolbarExtension
except ImportError:
    DebugToolbarExtension = None

from routes.rutas_autenticacion import bp_autenticacion
from routes.rutas_cliente import bp_cliente
from routes.rutas_admin import bp_admin
from routes.rutas_api import bp_api


def crear_app():
    """Fábrica de la aplicación Flask."""
    app = Flask(__name__)
    CORS(app)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'trespasos_secret_2026')
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    if DebugToolbarExtension:
        DebugToolbarExtension(app)

    # Registrar blueprints
    app.register_blueprint(bp_autenticacion)
    app.register_blueprint(bp_cliente)
    app.register_blueprint(bp_admin)
    app.register_blueprint(bp_api)

    return app


app = crear_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
