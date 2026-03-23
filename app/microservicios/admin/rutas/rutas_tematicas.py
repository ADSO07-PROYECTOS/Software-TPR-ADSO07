from flask import Blueprint, jsonify, request
from conexion import conectar

mod_tematicas = Blueprint('tematicas', __name__)


@mod_tematicas.route('/api/admin/tematicas', methods=['GET'])
def admin_listar_tematicas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "SELECT tematica_id, nombre_tematica, activo FROM tematicas ORDER BY nombre_tematica"
            )
        except Exception:
            cursor.execute("ALTER TABLE tematicas ADD COLUMN activo TINYINT(1) NOT NULL DEFAULT 1")
            conn.commit()
            cursor.execute(
                "SELECT tematica_id, nombre_tematica, activo FROM tematicas ORDER BY nombre_tematica"
            )
        tematicas = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(tematicas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_tematicas.route('/api/admin/tematicas/<int:tematica_id>', methods=['PUT'])
def admin_toggle_tematica(tematica_id):
    try:
        datos = request.get_json()
        activo = int(datos.get('activo', 1))
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tematicas SET activo = %s WHERE tematica_id = %s",
            (activo, tematica_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Temática actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_tematicas.route('/api/admin/tematicas', methods=['POST'])
def admin_agregar_tematica():
    try:
        datos = request.get_json()
        nombre = datos.get('nombre_tematica', '').strip()
        if not nombre:
            return jsonify({"error": "nombre_tematica es obligatorio"}), 400
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO tematicas (nombre_tematica) VALUES (%s)", (nombre,))
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close(); conn.close()
        return jsonify({"tematica_id": nuevo_id, "nombre_tematica": nombre}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_tematicas.route('/api/admin/tematicas/<int:tematica_id>', methods=['DELETE'])
def admin_eliminar_tematica(tematica_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tematicas WHERE tematica_id = %s", (tematica_id,))
        conn.commit()
        afectados = cursor.rowcount
        cursor.close(); conn.close()
        if afectados == 0:
            return jsonify({"error": "Temática no encontrada"}), 404
        return jsonify({"mensaje": "Temática eliminada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
