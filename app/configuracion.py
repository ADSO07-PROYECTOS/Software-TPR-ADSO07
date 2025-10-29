# configuracion.py
from flask import Flask
import os
from random import randint
from datetime import timedelta
import mysql.connector


def crear_app():
    """
    Crea y configura la aplicación Flask.
    """
    app = Flask(__name__)

    # 🔐 Clave secreta para sesiones
    app.secret_key = os.getenv("SECRET_KEY", str(randint(100000, 999999)))

    # ⏱ Duración de la sesión
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

    # 📦 Carpeta para subir archivos (si usas uploads)
    app.config["CARPETAUP"] = os.path.join(os.getcwd(), "uploads")

    # 🗄️ Configuración y conexión a la base de datos MySQL
    try:
        miDB = mysql.connector.connect(
            host="64.23.140.136",
            port=3306,
            user="admin",
            password="sEnaAdso07s",
            database="bd_tpr",
        )
        mi_cursor = miDB.cursor(dictionary=True)
        app.config["DB_CONNECTION"] = miDB
        app.config["DB_CURSOR"] = mi_cursor
        print("✅ Conexión a la base de datos establecida correctamente.")

    except mysql.connector.Error as err:
        print(f"❌ Error al conectar con la base de datos: {err}")
        miDB = None
        mi_cursor = None

    return app
