from flask import Blueprint, jsonify, request
from conexion import conectar

mod_clientes = Blueprint('clientes', __name__)

ROLES_VALIDOS = {'cliente', 'cajero', 'administrador'}


def normalizar_rol(valor, predeterminado='cliente'):
    rol = (valor or predeterminado).strip().lower()
    return rol if rol in ROLES_VALIDOS else predeterminado


@mod_clientes.route('/api/admin/clientes', methods=['GET'])
def admin_listar_clientes():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT cliente_id, cc_cliente, nombre, email, telefono, rol
            FROM clientes
            ORDER BY
                FIELD(rol, 'administrador', 'cajero', 'cliente'),
                nombre
            """
        )
        clientes = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(clientes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_clientes.route('/api/admin/clientes', methods=['POST'])
def admin_crear_cliente():
    datos = request.get_json() or {}
    cc_cliente = (datos.get('cc_cliente') or '').strip()
    nombre = (datos.get('nombre') or '').strip()
    email = (datos.get('email') or '').strip() or None
    telefono = (datos.get('telefono') or '').strip() or None
    rol = normalizar_rol(datos.get('rol'))

    if not cc_cliente or not nombre:
        return jsonify({"error": "La cédula y el nombre son obligatorios"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cliente_id FROM clientes WHERE cc_cliente = %s",
            (cc_cliente,)
        )
        existente = cursor.fetchone()
        if existente:
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe un usuario con esa cédula"}), 409

        cursor.execute(
            """
            INSERT INTO clientes (cc_cliente, nombre, email, telefono, rol)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (cc_cliente, nombre, email, telefono, rol)
        )
        nuevo_id = cursor.lastrowid
        conn.commit()

        cursor.execute(
            "SELECT cliente_id, cc_cliente, nombre, email, telefono, rol FROM clientes WHERE cliente_id = %s",
            (nuevo_id,)
        )
        cliente = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(cliente), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_clientes.route('/api/admin/clientes/<int:cliente_id>', methods=['PUT'])
def admin_actualizar_cliente(cliente_id):
    datos = request.get_json() or {}
    cc_cliente = (datos.get('cc_cliente') or '').strip()
    nombre = (datos.get('nombre') or '').strip()
    email = (datos.get('email') or '').strip() or None
    telefono = (datos.get('telefono') or '').strip() or None
    rol = normalizar_rol(datos.get('rol'))

    if not cc_cliente or not nombre:
        return jsonify({"error": "La cédula y el nombre son obligatorios"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cliente_id FROM clientes WHERE cliente_id = %s",
            (cliente_id,)
        )
        actual = cursor.fetchone()
        if not actual:
            cursor.close(); conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        cursor.execute(
            "SELECT cliente_id FROM clientes WHERE cc_cliente = %s AND cliente_id <> %s",
            (cc_cliente, cliente_id)
        )
        duplicado = cursor.fetchone()
        if duplicado:
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe otro usuario con esa cédula"}), 409

        cursor.execute(
            """
            UPDATE clientes
            SET cc_cliente = %s,
                nombre = %s,
                email = %s,
                telefono = %s,
                rol = %s
            WHERE cliente_id = %s
            """,
            (cc_cliente, nombre, email, telefono, rol, cliente_id)
        )
        conn.commit()

        cursor.execute(
            "SELECT cliente_id, cc_cliente, nombre, email, telefono, rol FROM clientes WHERE cliente_id = %s",
            (cliente_id,)
        )
        cliente = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(cliente)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_clientes.route('/api/admin/clientes/<int:cliente_id>', methods=['DELETE'])
def admin_eliminar_cliente(cliente_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE cliente_id = %s", (cliente_id,))
        conn.commit()
        afectados = cursor.rowcount
        cursor.close(); conn.close()
        if afectados == 0:
            return jsonify({"error": "Cliente no encontrado"}), 404
        return jsonify({"mensaje": "Cliente eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
