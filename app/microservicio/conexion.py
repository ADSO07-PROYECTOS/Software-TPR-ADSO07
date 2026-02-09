import mysql.connector
from mysql.connector import Error

def conectar():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host='64.23.140.136',
            user='usuario',
            password='Rest@uranteTPR?',
            database='db_tpr',
            auth_plugin='mysql_native_password'
        )
        
        if conexion.is_connected():
            print("Conexion exitosa a la base de datos")
        return conexion
    
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
