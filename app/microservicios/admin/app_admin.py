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


# ── Dashboard Stats ──────────────────────────────────────────────────────────

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
                    SUM(CASE WHEN r.reserva_id IS NOT NULL AND r.estado = 'confirmada' THEN 1 ELSE 0 END) AS reservadas,
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


# ── Clientes ─────────────────────────────────────────────────────────────────

@app.route('/api/admin/clientes', methods=['GET'])
def admin_listar_clientes():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cliente_id, cc_cliente, nombre, email, telefono FROM clientes ORDER BY nombre"
        )
        clientes = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(clientes)
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


# ── Productos (proxy → microservicio menu :5001) ──────────────────────────────

@app.route('/api/admin/productos', methods=['GET'])
def admin_listar_productos():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.producto_id, p.nombre_producto, p.precio_base,
                   p.descripcion_producto, p.disponibilidad_producto,
                   p.imagen_producto, c.nombre_categoria
            FROM productos p
            LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
            WHERE c.nombre_categoria NOT IN ('Sabores','tamanos','adiciones')
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
        resp = requests.get(f'{MENU_MS}/api/categorias', timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Domicilios ────────────────────────────────────────────────────────────────

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


# ── Reservas ──────────────────────────────────────────────────────────────────

@app.route('/api/admin/reservas', methods=['GET'])
def admin_listar_reservas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.estado,
                   r.pago_transferencia, m.piso,
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
        cursor.close(); conn.close()
        return jsonify(reservas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/reservas/<int:reserva_id>', methods=['PUT'])
def admin_actualizar_reserva(reserva_id):
    try:
        datos = request.get_json()
        nuevo_estado = datos.get('estado')
        if not nuevo_estado:
            return jsonify({"error": "estado requerido"}), 400
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reservas SET estado = %s WHERE reserva_id = %s",
            (nuevo_estado, reserva_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Estado actualizado"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Temáticas ─────────────────────────────────────────────────────────────────

@app.route('/api/admin/tematicas', methods=['GET'])
def admin_listar_tematicas():
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT tematica_id, nombre_tematica FROM tematicas ORDER BY nombre_tematica"
        )
        tematicas = cursor.fetchall()
        cursor.close(); conn.close()
        return jsonify(tematicas)
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


if __name__ == '__main__':
    app.run(debug=True, port=5006)
