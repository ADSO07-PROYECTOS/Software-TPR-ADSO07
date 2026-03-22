"""
Acceso a datos – Temáticas.
"""
from conexion import conectar


def obtener_tematicas():
    """Devuelve la lista de temáticas disponibles."""
    conexion = conectar()
    if not conexion:
        return []
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
        lista = cursor.fetchall()
    except Exception:
        cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
        lista = cursor.fetchall()
    cursor.close()
    conexion.close()
    return lista
