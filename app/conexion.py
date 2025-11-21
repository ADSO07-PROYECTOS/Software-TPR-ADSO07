import mysql.connector


def conectar():
    connection = mysql.connector.connect(
        host='64.23.140.136',
        user='usuario',
        password='Rest@uranteTPR?',
        database= 'db_tpr'
    )
    
    if connection != None:
        return connection
    else:
        print("La conexion no fue exitosa")

