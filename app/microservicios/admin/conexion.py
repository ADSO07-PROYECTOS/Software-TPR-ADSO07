import mysql.connector
from mysql.connector import Error

def conectar():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='taster',
            password='uYW8CXhOAC7',
            database='db_tpr'
        )
        if conexion.is_connected():
            print("Conexion exitosa a la base de datos")
        return conexion
    except Error as e:
        print(f"Error al conectar: {e}")
        return None
