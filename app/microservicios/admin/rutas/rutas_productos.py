from flask import Blueprint, jsonify, request
from conexion import conectar
import requests

MENU_MS = 'http://localhost:5001'

mod_productos = Blueprint('productos', __name__)


@mod_productos.route('/api/admin/productos', methods=['GET'])
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


@mod_productos.route('/api/admin/productos', methods=['POST'])
def admin_agregar_producto():
    try:
        resp = requests.post(f'{MENU_MS}/api/productos',
                             json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_productos.route('/api/admin/productos/<int:producto_id>', methods=['PUT'])
def admin_actualizar_producto(producto_id):
    try:
        resp = requests.put(f'{MENU_MS}/api/productos/{producto_id}',
                            json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_productos.route('/api/admin/productos/<int:producto_id>', methods=['DELETE'])
def admin_desactivar_producto(producto_id):
    try:
        resp = requests.delete(f'{MENU_MS}/api/productos/{producto_id}', timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Categorías ──────────────────────────────────────────

@mod_productos.route('/api/admin/categorias', methods=['GET'])
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


@mod_productos.route('/api/admin/categorias', methods=['POST'])
def admin_crear_categoria():
    try:
        resp = requests.post(f'{MENU_MS}/api/categorias',
                             json=request.get_json(), timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mod_productos.route('/api/admin/categorias/<int:cat_id>', methods=['PUT'])
def admin_editar_categoria(cat_id):
    try:
        datos = request.get_json()
        nombre = datos.get('nombre_categoria', '').strip()
        imagen = datos.get('imagen_categoria', None)
        if not nombre:
            return jsonify({"error": "nombre_categoria es obligatorio"}), 400
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT categoria_id FROM categorias WHERE LOWER(nombre_categoria) = LOWER(%s) AND categoria_id != %s",
            (nombre, cat_id)
        )
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"error": "Ya existe una categoría con ese nombre"}), 409
        cursor.execute(
            "UPDATE categorias SET nombre_categoria=%s, imagen_categoria=%s WHERE categoria_id=%s",
            (nombre, imagen, cat_id)
        )
        conn.commit()
        cursor.close(); conn.close()
        return jsonify({"mensaje": "Categoría actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
