"""
Acceso a datos – Reservas.
"""
from conexion import conectar


def obtener_reserva_con_tematica(id_reserva):
    """Devuelve la reserva unida a su temática, o None."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.*, t.nombre_tematica
        FROM reservas r
        LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
        WHERE r.reserva_id = %s
    """, (id_reserva,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()
    return reserva


def obtener_productos_reserva(id_reserva):
    """Devuelve la lista de productos asociados a una reserva."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT dr.cantidad, dr.valor_unitario, p.nombre_producto
        FROM detalles_reservas dr
        JOIN productos p ON dr.producto_id = p.producto_id
        WHERE dr.reserva_id = %s
    """, (id_reserva,))
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return productos


def obtener_reservas_por_cedula(cedula):
    """Devuelve las reservas de un cliente identificado por cédula."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.estado,
               c.nombre, c.email, c.telefono, c.cc_cliente,
               t.nombre_tematica, m.piso
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.cliente_id
        LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
        LEFT JOIN mesas m ON r.mesa_id = m.mesa_id
        WHERE c.cc_cliente = %s
        ORDER BY r.fecha_hora DESC
    """, (cedula,))
    reservas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return reservas


def obtener_pedido_reserva(id_reserva):
    """Devuelve los productos del pedido de una reserva."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.nombre_producto, dr.cantidad, dr.notas
        FROM detalles_reservas dr
        JOIN productos p ON dr.producto_id = p.producto_id
        WHERE dr.reserva_id = %s
    """, (id_reserva,))
    pedido = cursor.fetchall()
    cursor.close()
    conexion.close()
    return pedido


def eliminar_reserva_por_id(id_reserva):
    """Elimina la reserva y sus detalles. Devuelve True si tuvo éxito."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM detalles_reservas WHERE reserva_id = %s", (id_reserva,))
    cursor.execute("DELETE FROM reservas WHERE reserva_id = %s", (id_reserva,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return True


def obtener_reserva_para_modificar(id_reserva):
    """Devuelve la reserva con datos del cliente para el formulario de edición."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.tematica_id, r.estado,
               c.nombre, c.email, c.telefono, c.cc_cliente
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.cliente_id
        WHERE r.reserva_id = %s
    """, (id_reserva,))
    reserva = cursor.fetchone()
    cursor.close()
    conexion.close()
    return reserva


def actualizar_reserva(id_reserva, fecha_hora, personas, tematica, nombre, email, telefono):
    """Actualiza los datos de una reserva y del cliente asociado."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE reservas
        SET fecha_hora = %s, cantidad_personas = %s, tematica_id = %s
        WHERE reserva_id = %s
    """, (fecha_hora, personas, tematica, id_reserva))
    cursor.execute("""
        UPDATE clientes c
        JOIN reservas r ON r.cliente_id = c.cliente_id
        SET c.nombre = %s, c.email = %s, c.telefono = %s
        WHERE r.reserva_id = %s
    """, (nombre, email, telefono, id_reserva))
    conexion.commit()
    cursor.close()
    conexion.close()


def obtener_cedula_por_reserva(id_reserva):
    """Devuelve la cédula del cliente asociada a una reserva."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.cc_cliente
        FROM reservas r
        JOIN clientes c ON r.cliente_id = c.cliente_id
        WHERE r.reserva_id = %s
    """, (id_reserva,))
    resultado = cursor.fetchone()
    cursor.close()
    conexion.close()
    return resultado['cc_cliente'] if resultado else None


def guardar_comprobante_reserva(id_reserva, ruta_relativa):
    """Guarda la ruta del comprobante y marca la reserva como 'en espera'."""
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SHOW COLUMNS FROM reservas LIKE 'comprobante_transferencia'")
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE reservas ADD COLUMN comprobante_transferencia VARCHAR(255) NULL")
        conexion.commit()
    cursor.execute(
        "UPDATE reservas SET comprobante_transferencia=%s, pago_transferencia=1, estado='en espera' WHERE reserva_id=%s",
        (ruta_relativa, id_reserva)
    )
    conexion.commit()
    cursor.close()
    conexion.close()
