"""
Acceso a datos – Domicilios.
"""
from conexion import conectar


def obtener_domicilio_por_id(id_domicilio):
    """Devuelve un dict con los datos del domicilio o None."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM domicilios WHERE domicilio_id = %s", (id_domicilio,))
    domicilio = cursor.fetchone()
    cursor.close()
    conexion.close()
    return domicilio


def obtener_productos_domicilio(id_domicilio):
    """Devuelve la lista de productos asociados a un domicilio."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT dd.cantidad, dd.valor_unitario, p.nombre_producto
        FROM detalles_domicilios dd
        JOIN productos p ON dd.producto_id = p.producto_id
        WHERE dd.domicilio_id = %s
    """, (id_domicilio,))
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return productos


def obtener_cedula_por_domicilio(id_domicilio):
    """Devuelve la cédula del cliente asociada a un domicilio."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.cc_cliente
        FROM domicilios d
        JOIN clientes c ON d.cliente_id = c.cliente_id
        WHERE d.domicilio_id = %s
    """, (id_domicilio,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado['cc_cliente'] if resultado else None


def guardar_comprobante_domicilio(id_domicilio, ruta_relativa):
    """Guarda la ruta del comprobante y marca el domicilio como 'En revisión'."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SHOW COLUMNS FROM domicilios LIKE 'comprobante_transferencia'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE domicilios ADD COLUMN comprobante_transferencia VARCHAR(255) NULL")
        conexion.commit()
    cursor.execute(
        "UPDATE domicilios SET comprobante_transferencia=%s, estado_pedido='En revisión' WHERE domicilio_id=%s",
        (ruta_relativa, id_domicilio)
    )
    conexion.commit()
    cursor.close()
    conexion.close()
