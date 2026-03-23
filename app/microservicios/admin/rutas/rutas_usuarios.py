from flask import Blueprint, jsonify, request
from conexion import conectar

mod_usuarios = Blueprint('usuarios', __name__)


@mod_usuarios.route('/api/admin/usuarios', methods=['GET'])
def admin_listar_usuarios():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT usuario_id, cc_usuario, nombre, apellidos, email, telefono, rol, estado "
            "FROM usuarios ORDER BY FIELD(rol,'administrador','cajero'), nombre"
        )
        usuarios = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_usuarios.route('/api/admin/usuarios', methods=['POST'])
def admin_crear_usuario():
    datos = request.get_json() or {}
    cc_usuario  = (datos.get('cc_usuario') or '').strip()
    nombre      = (datos.get('nombre') or '').strip()
    apellidos   = (datos.get('apellidos') or '').strip()
    email       = (datos.get('email') or '').strip() or None
    telefono    = (datos.get('telefono') or '').strip() or None
    rol         = (datos.get('rol') or '').strip().lower()
    contrasena  = (datos.get('contrasena') or '').strip()

    if not cc_usuario or not nombre or not contrasena:
        return jsonify({"error": "Cédula, nombre y contraseña son obligatorios"}), 400
    if rol not in ('administrador', 'cajero'):
        return jsonify({"error": "El rol debe ser administrador o cajero"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT usuario_id FROM usuarios WHERE cc_usuario = %s", (cc_usuario,))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe un usuario con esa cédula"}), 409

        cursor.execute(
            "INSERT INTO usuarios (cc_usuario, nombre, apellidos, email, telefono, rol, contrasena) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (cc_usuario, nombre, apellidos, email, telefono, rol, contrasena)
        )
        nuevo_id = cursor.lastrowid
        conn.commit()
        cursor.execute(
            "SELECT usuario_id, cc_usuario, nombre, apellidos, email, telefono, rol, estado "
            "FROM usuarios WHERE usuario_id = %s", (nuevo_id,)
        )
        usuario = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(usuario), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_usuarios.route('/api/admin/usuarios/<int:usuario_id>', methods=['PUT'])
def admin_actualizar_usuario(usuario_id):
    datos = request.get_json() or {}
    cc_usuario  = (datos.get('cc_usuario') or '').strip()
    nombre      = (datos.get('nombre') or '').strip()
    apellidos   = (datos.get('apellidos') or '').strip()
    email       = (datos.get('email') or '').strip() or None
    telefono    = (datos.get('telefono') or '').strip() or None
    rol         = (datos.get('rol') or '').strip().lower()
    contrasena  = (datos.get('contrasena') or '').strip()
    estado      = int(datos.get('estado', 1))

    if not cc_usuario or not nombre:
        return jsonify({"error": "Cédula y nombre son obligatorios"}), 400
    if rol not in ('administrador', 'cajero'):
        return jsonify({"error": "El rol debe ser administrador o cajero"}), 400

    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT usuario_id FROM usuarios WHERE usuario_id = %s", (usuario_id,))
        if not cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Usuario no encontrado"}), 404

        cursor.execute(
            "SELECT usuario_id FROM usuarios WHERE cc_usuario = %s AND usuario_id <> %s",
            (cc_usuario, usuario_id)
        )
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe otro usuario con esa cédula"}), 409

        if contrasena:
            cursor.execute(
                "UPDATE usuarios SET cc_usuario=%s, nombre=%s, apellidos=%s, email=%s, "
                "telefono=%s, rol=%s, estado=%s, contrasena=%s WHERE usuario_id=%s",
                (cc_usuario, nombre, apellidos, email, telefono, rol, estado, contrasena, usuario_id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET cc_usuario=%s, nombre=%s, apellidos=%s, email=%s, "
                "telefono=%s, rol=%s, estado=%s WHERE usuario_id=%s",
                (cc_usuario, nombre, apellidos, email, telefono, rol, estado, usuario_id)
            )
        conn.commit()
        cursor.execute(
            "SELECT usuario_id, cc_usuario, nombre, apellidos, email, telefono, rol, estado "
            "FROM usuarios WHERE usuario_id = %s", (usuario_id,)
        )
        usuario = cursor.fetchone()
        cursor.close(); conn.close()
        return jsonify(usuario)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_usuarios.route('/api/admin/usuarios/<int:usuario_id>', methods=['DELETE'])
def admin_eliminar_usuario(usuario_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE usuario_id = %s", (usuario_id,))
        conn.commit()
        afectados = cursor.rowcount
        cursor.close(); conn.close()
        if afectados == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"mensaje": "Usuario eliminado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
