from flask import Blueprint, jsonify, request
from conexion import conectar

mod_pedidos = Blueprint('pedidos', __name__)


@mod_pedidos.route('/api/admin/domicilios', methods=['GET'])
def admin_listar_domicilios():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.domicilio_id, d.direccion, d.estado_pedido,
                   d.pago_transferencia, d.fecha_hora,
                   d.comprobante_transferencia,
                   c.nombre, c.telefono, c.email,
                   SUM(dd.cantidad * dd.valor_unitario) AS total
            FROM domicilios d
            LEFT JOIN clientes c ON d.cliente_id = c.cliente_id
            LEFT JOIN detalles_domicilios dd ON d.domicilio_id = dd.domicilio_id
            GROUP BY d.domicilio_id
            ORDER BY d.fecha_hora DESC
        """)
        domicilios = cursor.fetchall()
        for d in domicilios:
            if d.get('fecha_hora'):
                d['fecha_hora'] = str(d['fecha_hora'])
            if d.get('total') is not None:
                d['total'] = float(d['total'])
            d['pago_transferencia'] = int(d.get('pago_transferencia') or 0)
        cursor.close(); conn.close()
        return jsonify(domicilios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_pedidos.route('/api/admin/domicilios/<int:domicilio_id>', methods=['PUT'])
def admin_actualizar_domicilio(domicilio_id):
    try:
        datos = request.get_json()
        nuevo_estado = datos.get('estado_pedido')
        comprobante_validado = datos.get('comprobante_validado')
        if not nuevo_estado:
            return jsonify({"error": "estado_pedido requerido"}), 400
        conn = conectar()
        cursor = conn.cursor()
        if comprobante_validado:
            cursor.execute(
                "UPDATE domicilios SET estado_pedido = %s, comprobante_transferencia = NULL WHERE domicilio_id = %s",
                (nuevo_estado, domicilio_id)
            )
        else:
            cursor.execute(
                "UPDATE domicilios SET estado_pedido = %s WHERE domicilio_id = %s",
                (nuevo_estado, domicilio_id)
            )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Estado actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Reservas ────────────────────────────────────────────

@mod_pedidos.route('/api/admin/reservas', methods=['GET'])
def admin_listar_reservas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.estado,
                   r.pago_transferencia, m.piso,
                   r.comprobante_transferencia,
                   c.nombre, c.telefono, c.email, c.cc_cliente,
                   t.nombre_tematica
            FROM reservas r
            LEFT JOIN clientes c ON r.cliente_id = c.cliente_id
            LEFT JOIN mesas m ON r.mesa_id = m.mesa_id
            LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
            ORDER BY r.fecha_hora DESC
        """)
        reservas = cursor.fetchall()
        for rv in reservas:
            if rv.get('fecha_hora'):
                rv['fecha_hora'] = str(rv['fecha_hora'])
            rv['pago_transferencia'] = int(rv.get('pago_transferencia') or 0)
        cursor.close(); conn.close()
        return jsonify(reservas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_pedidos.route('/api/admin/reservas/<int:reserva_id>', methods=['PUT'])
def admin_actualizar_reserva(reserva_id):
    try:
        datos = request.get_json()
        nuevo_estado = datos.get('estado')
        comprobante_validado = datos.get('comprobante_validado')
        if not nuevo_estado:
            return jsonify({"error": "estado requerido"}), 400
        conn = conectar()
        cursor = conn.cursor()

        if comprobante_validado:
            cursor.execute(
                "UPDATE reservas SET estado = %s, comprobante_transferencia = NULL WHERE reserva_id = %s",
                (nuevo_estado, reserva_id)
            )
        else:
            cursor.execute(
                "UPDATE reservas SET estado = %s WHERE reserva_id = %s",
                (nuevo_estado, reserva_id)
            )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Estado actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
