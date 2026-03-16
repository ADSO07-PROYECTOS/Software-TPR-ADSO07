"""
Microservicio Admin – Tres Pasos
Puerto: 5006
Rutas: /api/admin/*
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from conexion import conectar
import requests

MENU_MS = 'http://localhost:5001'

app = Flask(__name__)
CORS(app)

ROLES_VALIDOS = {'cliente', 'cajero', 'administrador'}

def normalizar_rol(valor, predeterminado='cliente'):
    rol = (valor or predeterminado).strip().lower()
    return rol if rol in ROLES_VALIDOS else predeterminado

def asegurar_columna_rol():
    conn = conectar()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM clientes LIKE 'rol'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE clientes
                ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'cliente'
            """)
            conn.commit()

        cursor.execute("""
            UPDATE clientes
            SET rol = 'cliente'
            WHERE rol IS NULL OR TRIM(rol) = ''
        """)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

asegurar_columna_rol()

@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    stats = {
        'domicilios_hoy': 0, 'domicilios_pendientes': 0,
        'mesas_disponibles': 0, 'mesas_ocupadas': 0, 'mesas_reservadas': 0,
    }
    mesas_por_piso = []
    pedidos_recientes = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) AS c FROM domicilios WHERE DATE(fecha_hora) = CURDATE()"
            )
            row = cursor.fetchone()
            stats['domicilios_hoy'] = row['c'] if row else 0

            cursor.execute(
                "SELECT COUNT(*) AS c FROM domicilios WHERE estado_pedido = 'Pendiente'"
            )
            row = cursor.fetchone()
            stats['domicilios_pendientes'] = row['c'] if row else 0

            cursor.execute("""
                SELECT m.piso,
                    COUNT(*) AS total,
                    SUM(CASE WHEN r.reserva_id IS NOT NULL AND r.estado IN ('confirmada', 'en espera') THEN 1 ELSE 0 END) AS reservadas,
                    SUM(CASE WHEN r.reserva_id IS NOT NULL AND r.estado = 'ocupada'    THEN 1 ELSE 0 END) AS ocupadas
                FROM mesas m
                LEFT JOIN reservas r ON m.mesa_id = r.mesa_id AND DATE(r.fecha_hora) = CURDATE()
                GROUP BY m.piso
                ORDER BY m.piso
            """)
            for fila in cursor.fetchall():
                reservadas  = int(fila['reservadas'] or 0)
                ocupadas    = int(fila['ocupadas']   or 0)
                total       = int(fila['total'])
                disponibles = max(total - reservadas - ocupadas, 0)
                mesas_por_piso.append({
                    'piso': fila['piso'],
                    'total': total,
                    'reservadas': reservadas,
                    'ocupadas': ocupadas,
                    'disponibles': disponibles,
                })
                stats['mesas_disponibles'] += disponibles
                stats['mesas_ocupadas']    += ocupadas
                stats['mesas_reservadas']  += reservadas

            cursor.execute("""
                SELECT d.domicilio_id, d.estado_pedido, d.fecha_hora,
                       c.nombre, d.direccion
                FROM domicilios d
                LEFT JOIN clientes c ON d.cliente_id = c.cliente_id
                ORDER BY d.fecha_hora DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                row['fecha_hora'] = str(row['fecha_hora']) if row.get('fecha_hora') else None
                pedidos_recientes.append(row)

            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        'stats': stats,
        'mesas_por_piso': mesas_por_piso,
        'pedidos_recientes': pedidos_recientes,
    })

@app.route('/api/admin/clientes', methods=['GET'])
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

@app.route('/api/admin/clientes', methods=['POST'])
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

@app.route('/api/admin/clientes/<int:cliente_id>', methods=['PUT'])
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

@app.route('/api/admin/clientes/<int:cliente_id>', methods=['DELETE'])
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

@app.route('/api/admin/productos', methods=['GET'])
def admin_listar_productos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.producto_id, p.nombre_producto, p.categoria_id, p.precio_base,
                   p.descripcion_producto, p.disponibilidad_producto,
                   p.imagen_producto, p.stock, c.nombre_categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
            WHERE c.nombre_categoria NOT IN ('Sabores','tamanos')
               OR c.nombre_categoria IS NULL
            ORDER BY p.nombre_producto
        """)
        productos = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/productos', methods=['POST'])
def admin_agregar_producto():
    try:
        resp = requests.post(f'{MENU_MS}/api/productos',
                             json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/productos/<int:producto_id>', methods=['PUT'])
def admin_actualizar_producto(producto_id):
    try:
        resp = requests.put(f'{MENU_MS}/api/productos/{producto_id}',
                            json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/productos/<int:producto_id>', methods=['DELETE'])
def admin_desactivar_producto(producto_id):
    try:
        resp = requests.delete(f'{MENU_MS}/api/productos/{producto_id}', timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/categorias', methods=['GET'])
def admin_listar_categorias():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT categoria_id, nombre_categoria, imagen_categoria "
            "FROM categorias "
            "WHERE nombre_categoria NOT IN ('Sabores', 'tamanos') "
            "ORDER BY categoria_id"
        )
        rows = cursor.fetchall()
        cursor.close(); conn.close()
        categorias = [{'id': r['categoria_id'], 'nombre': r['nombre_categoria'], 'imagen': r['imagen_categoria']} for r in rows]
        return jsonify(categorias)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/categorias', methods=['POST'])
def admin_crear_categoria():
    try:
        resp = requests.post(f'{MENU_MS}/api/categorias',
                             json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/categorias/<int:cat_id>', methods=['PUT'])
def admin_editar_categoria(cat_id):
    try:
        datos = request.get_json()
        nombre = datos.get('nombre_categoria', '').strip()
        imagen = datos.get('imagen_categoria', None)
        if not nombre:
            return jsonify({"error": "nombre_categoria es obligatorio"}), 400
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE categorias SET nombre_categoria=%s, imagen_categoria=%s WHERE categoria_id=%s",
            (nombre, imagen, cat_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Categoría actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/domicilios', methods=['GET'])
def admin_listar_domicilios():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.domicilio_id, d.direccion, d.estado_pedido,
                   d.pago_transferencia, d.fecha_hora,
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

@app.route('/api/admin/domicilios/<int:domicilio_id>', methods=['PUT'])
def admin_actualizar_domicilio(domicilio_id):
    try:
        datos = request.get_json()
        nuevo_estado = datos.get('estado_pedido')
        if not nuevo_estado:
            return jsonify({"error": "estado_pedido requerido"}), 400
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE domicilios SET estado_pedido = %s WHERE domicilio_id = %s",
            (nuevo_estado, domicilio_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Estado actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/reservas', methods=['GET'])
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

@app.route('/api/admin/reservas/<int:reserva_id>', methods=['PUT'])
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

@app.route('/api/admin/tematicas', methods=['GET'])
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

@app.route('/api/admin/tematicas/<int:tematica_id>', methods=['PUT'])
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
        return jsonify({"mensaje": "Tem\u00e1tica actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/tematicas', methods=['POST'])
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

@app.route('/api/admin/tematicas/<int:tematica_id>', methods=['DELETE'])
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

@app.route('/api/admin/usuarios', methods=['GET'])
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

@app.route('/api/admin/usuarios', methods=['POST'])
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

@app.route('/api/admin/usuarios/<int:usuario_id>', methods=['PUT'])
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

@app.route('/api/admin/usuarios/<int:usuario_id>', methods=['DELETE'])
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5006)
