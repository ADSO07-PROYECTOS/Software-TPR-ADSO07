import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        conexion = mysql.connector.connect(
            host='64.23.140.136',
            user='usuario',
            password='Rest@uranteTPR?',
            database= 'db_tpr1'
        )


        return conexion
    except Error as e:
        print(f"Error al conectar: {e}")
        return None