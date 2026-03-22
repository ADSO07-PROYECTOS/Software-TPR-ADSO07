"""
Acceso a datos – Clientes.
"""
from conexion import conectar


def obtener_cliente_por_id(id_cliente):
    """Devuelve un dict con los datos del cliente o None."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (id_cliente,))
    cliente = cursor.fetchone()
    cursor.close()
    conexion.close()
    return cliente
