"""
Acceso a datos – Usuarios del panel (admin/cajero).
"""
from conexion import conectar


def buscar_usuario_por_credenciales(nombre, contrasena):
    """Busca un usuario admin/cajero por nombre y contraseña. Devuelve dict o None."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT usuario_id, nombre, apellidos, rol FROM usuarios "
        "WHERE nombre = %s AND contrasena = %s AND estado = 1 AND rol IN ('administrador','cajero')",
        (nombre, contrasena)
    )
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario
