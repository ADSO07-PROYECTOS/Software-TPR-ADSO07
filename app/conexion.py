# configuracion.py
from flask import Flask, g
import os
from random import randint
from datetime import timedelta
import mysql.connector
from mysql.connector import Error

# 🗄️ Configuración de la base de datos remota
DB_CONFIG = {
    "host": "64.23.140.136",  # IP de tu VPS
    "port": 3306,
    "user": "admin",
    "password": "sEnaAdso07s",
    "database": "db_tpr"
}

def obtener_conexion():
    """Crea y retorna una nueva conexión a la base de datos."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        return conexion
    except Error as e:
        print(f"❌ Error al obtener conexión: {e}")
        return None


def verificar_conexion():
    """Verifica si la base de datos está accesible."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        if conexion.is_connected():
            print("✅ Conexión exitosa a MySQL remoto.")
            conexion.close()
            return True
    except Error as e:
        print(f"❌ Error al conectar con MySQL: {e}")
    return False


def crear_conexion():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", str(randint(100000, 999999)))
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)
    app.config["CARPETAUP"] = os.path.join(os.getcwd(), "uploads")

    print("\n🔄 Verificando conexión a la base de datos...")
    if verificar_conexion():
        app.config["DB_CONFIG"] = DB_CONFIG
        print("✅ Flask configurado con acceso a la base de datos.\n")
    else:
        print("❌ No se pudo establecer conexión.\n")

    @app.before_request
    def before_request():
        """Abre una conexión por solicitud"""
        g.db = obtener_conexion()

    @app.teardown_appcontext
    def teardown_db(exception):
        """Cierra la conexión al terminar la solicitud"""
        db = getattr(g, "db", None)
        if db is not None and db.is_connected():
            db.close()

    return app

