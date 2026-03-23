from flask import Blueprint, jsonify, request
from conexion import conectar

mod_mesas = Blueprint('mesas', __name__)


@mod_mesas.route('/api/admin/mesas', methods=['GET'])
def admin_listar_mesas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT mesa_id, COALESCE(NULLIF(numero_mesa, 0), mesa_id) AS numero_mesa, piso "
            "FROM mesas ORDER BY piso, numero_mesa"
        )
        mesas = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(mesas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_mesas.route('/api/admin/mesas', methods=['POST'])
def admin_crear_mesa():
    datos = request.get_json() or {}
    numero_mesa = datos.get('numero_mesa')
    piso        = datos.get('piso')

    if not numero_mesa or not piso:
        return jsonify({"error": "numero_mesa y piso son obligatorios"}), 400
    if int(piso) not in (1, 2):
        return jsonify({"error": "El piso debe ser 1 o 2"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT mesa_id FROM mesas WHERE numero_mesa = %s AND piso = %s",
            (numero_mesa, piso)
        )
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe una mesa con ese número en ese piso"}), 409

        cursor.execute(
            "INSERT INTO mesas (numero_mesa, piso) VALUES (%s, %s)",
            (numero_mesa, piso)
        )
        nueva_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT mesa_id, numero_mesa, piso FROM mesas WHERE mesa_id = %s",
            (nueva_id,)
        )
        mesa = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(mesa), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_mesas.route('/api/admin/mesas/<int:mesa_id>', methods=['PUT'])
def admin_actualizar_mesa(mesa_id):
    datos = request.get_json() or {}
    numero_mesa = datos.get('numero_mesa')
    piso        = datos.get('piso')

    if not numero_mesa or not piso:
        return jsonify({"error": "numero_mesa y piso son obligatorios"}), 400
    if int(piso) not in (1, 2):
        return jsonify({"error": "El piso debe ser 1 o 2"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT mesa_id FROM mesas WHERE mesa_id = %s", (mesa_id,))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Mesa no encontrada"}), 404

        cursor.execute(
            "SELECT mesa_id FROM mesas WHERE numero_mesa = %s AND piso = %s AND mesa_id <> %s",
            (numero_mesa, piso, mesa_id)
        )
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe otra mesa con ese número en ese piso"}), 409

        cursor.execute(
            "UPDATE mesas SET numero_mesa=%s, piso=%s WHERE mesa_id=%s",
            (numero_mesa, piso, mesa_id)
        )
        conn.commit()
        cursor.execute(
            "SELECT mesa_id, numero_mesa, piso FROM mesas WHERE mesa_id = %s",
            (mesa_id,)
        )
        mesa = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(mesa)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_mesas.route('/api/admin/mesas/<int:mesa_id>', methods=['DELETE'])
def admin_eliminar_mesa(mesa_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) AS c FROM reservas WHERE mesa_id = %s", (mesa_id,)
        )
        row = cursor.fetchone()
        if row and row[0] > 0:
            cursor.close(); conn.close()
            return jsonify({"error": "No se puede eliminar: la mesa tiene reservas asociadas"}), 409

        cursor.execute("DELETE FROM mesas WHERE mesa_id = %s", (mesa_id,))
        conn.commit()
        afectados = cursor.rowcount
        cursor.close(); conn.close()
        if afectados == 0:
            return jsonify({"error": "Mesa no encontrada"}), 404
        return jsonify({"mensaje": "Mesa eliminada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
