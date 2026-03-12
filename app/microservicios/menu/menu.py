from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from conexion import conectar 

app = Flask(__name__)
CORS(app)

@app.route('/api/categorias', methods=['GET'])
def ver_menu():
    lista_categorias = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT categoria_id, nombre_categoria, imagen_categoria, tamano FROM categorias WHERE nombre_categoria != 'Sabores' AND nombre_categoria != 'tamanos' AND nombre_categoria != 'adiciones'")
            result = cursor.fetchall()
            
            for row in result:
                categoria = {
                    'id': row['categoria_id'],
                    'nombre': row['nombre_categoria'],
                    'imagen': row['imagen_categoria'],
                    'tamano': row['tamano']
                }
                lista_categorias.append(categoria)
            
            cursor.close()
            conn.close()

        return jsonify(lista_categorias)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/categorias', methods=['POST'])
def crear_categoria():
    try:
        datos = request.get_json()
        nombre = datos.get('nombre_categoria', '').strip()
        imagen = datos.get('imagen_categoria', None)
        if not nombre:
            return jsonify({"error": "nombre_categoria es obligatorio"}), 400
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categorias (nombre_categoria, imagen_categoria) VALUES (%s, %s)",
                (nombre, imagen)
            )
            conn.commit()
            nuevo_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return jsonify({"mensaje": "Categoría creada", "categoria_id": nuevo_id}), 201
        return jsonify({"error": "Sin conexión a BD"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/platos/<int:id_categoria>', methods=['GET'])
def ver_platos_por_categoria(id_categoria):
    lista_platos = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT * FROM productos WHERE categoria_id = %s AND disponibilidad_producto = 1"
            cursor.execute(query, (id_categoria,))
            result = cursor.fetchall()
            
            for row in result:
                plato = {
                    'id': row.get('producto_id'), 
                    'nombre': row.get('nombre_producto'),
                    'precio': row.get('precio_base'),
                    'descripcion': row.get('descripcion_producto'),
                    'imagen': row.get('imagen_producto'),
                    'categoria_id': row.get('categoria_id')
                }
                lista_platos.append(plato)
            
            cursor.close()
            conn.close()

        return jsonify(lista_platos)

    except Exception as e:
        print(f"Error en microservicio platos: {e}")
        return jsonify({"error": str(e)}), 500
    

# -- Obtener un solo plato por su ID ---
@app.route('/api/plato/<int:id_plato>', methods=['GET'])
def ver_detalle_plato(id_plato):
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT p.*, c.nombre_categoria
                FROM productos p
                LEFT JOIN categorias c ON p.categoria_id = c.categoria_id
                WHERE p.producto_id = %s
            """
            cursor.execute(query, (id_plato,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()

            if row:
                plato = {
                    'id': row.get('producto_id'), 
                    'nombre': row.get('nombre_producto'),
                    'precio': row.get('precio_base'),
                    'descripcion': row.get('descripcion_producto'),
                    'imagen': row.get('imagen_producto'),
                    'categoria_id': row.get('categoria_id'),
                    'categoria_nombre': row.get('nombre_categoria', '')
                }
                return jsonify(plato)
            else:
                return jsonify({"error": "Plato no encontrado"}), 404

    except Exception as e:
        print(f"Error buscando plato: {e}")
        return jsonify({"error": str(e)}), 500


# -- Agregar un nuevo producto --
@app.route('/api/productos', methods=['POST'])
def agregar_producto():
    try:
        datos = request.get_json()
        nombre    = datos.get('nombre_producto')
        categoria = datos.get('categoria_id')
        descripcion = datos.get('descripcion_producto', '')
        precio    = datos.get('precio_base', 0)
        imagen    = datos.get('imagen_producto', None)
        disponibilidad = datos.get('disponibilidad_producto', 1)

        if not nombre or not categoria:
            return jsonify({"error": "nombre_producto y categoria_id son obligatorios"}), 400

        conn = conectar()
        if conn:
            cursor = conn.cursor()
            query = """
                INSERT INTO productos
                    (nombre_producto, categoria_id, descripcion_producto, precio_base, imagen_producto, disponibilidad_producto)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nombre, categoria, descripcion, precio, imagen, disponibilidad))
            conn.commit()
            nuevo_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return jsonify({"mensaje": "Producto agregado correctamente", "producto_id": nuevo_id}), 201

        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    except Exception as e:
        print(f"Error al agregar producto: {e}")
        return jsonify({"error": str(e)}), 500


# -- Actualizar un producto existente --
@app.route('/api/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    try:
        datos = request.get_json()
        campos = []
        valores = []

        if 'nombre_producto' in datos:
            campos.append('nombre_producto = %s')
            valores.append(datos['nombre_producto'])
        if 'categoria_id' in datos:
            campos.append('categoria_id = %s')
            valores.append(datos['categoria_id'])
        if 'descripcion_producto' in datos:
            campos.append('descripcion_producto = %s')
            valores.append(datos['descripcion_producto'])
        if 'precio_base' in datos:
            campos.append('precio_base = %s')
            valores.append(datos['precio_base'])
        if 'imagen_producto' in datos:
            campos.append('imagen_producto = %s')
            valores.append(datos['imagen_producto'])
        if 'disponibilidad_producto' in datos:
            campos.append('disponibilidad_producto = %s')
            valores.append(datos['disponibilidad_producto'])

        if not campos:
            return jsonify({"error": "No hay campos para actualizar"}), 400

        valores.append(id_producto)
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            query = f"UPDATE productos SET {', '.join(campos)} WHERE producto_id = %s"
            cursor.execute(query, valores)
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({"mensaje": "Producto actualizado correctamente"}), 200

        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        return jsonify({"error": str(e)}), 500


# -- Desactivar un producto (soft delete) --
# No se elimina físicamente para preservar el historial de reservas y pedidos.
@app.route('/api/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE productos SET disponibilidad_producto = 0 WHERE producto_id = %s",
                (id_producto,)
            )
            conn.commit()
            afectados = cursor.rowcount
            cursor.close()
            conn.close()
            if afectados == 0:
                return jsonify({"error": "Producto no encontrado"}), 404
            return jsonify({"mensaje": "Producto desactivado correctamente"}), 200

        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    except Exception as e:
        print(f"Error al desactivar producto: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/extras', methods=['GET'])
def obtener_extras_configuracion():
    datos = {
        "tamanos": [],
        "adiciones": [],
        "sabores": []
    }
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # 1. Obtener Tamaños: productos de la categoría "tamano".
            # limite_sabores se extrae del número en descripcion_producto (ej: "Capacidad: 3 sabores" → 3)
            cursor.execute("""
                SELECT p.producto_id AS id,
                       p.nombre_producto AS nombre,
                       p.precio_base AS precio,
                       CAST(REGEXP_SUBSTR(p.descripcion_producto, '[0-9]+') AS UNSIGNED) AS limite_sabores
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.categoria_id
                WHERE LOWER(c.nombre_categoria) LIKE '%tamano%'
                  AND p.disponibilidad_producto = 1
                ORDER BY p.precio_base ASC
            """)
            datos["tamanos"] = cursor.fetchall()

            # 2. Obtener Sabores/Toppings (categoría "Sabores").
            # No se filtra por disponibilidad porque son toppings, no productos del menú principal.
            cursor.execute("""
                SELECT p.producto_id AS id,
                       p.nombre_producto AS nombre,
                       p.precio_base AS precio
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.categoria_id
                WHERE LOWER(c.nombre_categoria) LIKE '%sabor%'
            """)
            datos["sabores"] = cursor.fetchall()

            # 3. Adiciones (toppings extra como queso, piña, etc.)
            cursor.execute("""
                SELECT p.producto_id AS id,
                       p.nombre_producto AS nombre,
                       p.precio_base AS precio
                FROM productos p
                INNER JOIN categorias c ON p.categoria_id = c.categoria_id
                WHERE LOWER(c.nombre_categoria) LIKE '%adicion%'
                  AND p.disponibilidad_producto = 1
            """)
            datos["adiciones"] = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
        return jsonify(datos)

    except Exception as e:
        print(f"Error obteniendo extras: {e}")
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    try:
        print("--INICIANDO MICROSERVICIO DE MENU EN EL PUERTO 5001 --")
        app.run(debug=True, port=5001, host='0.0.0.0')
    except Exception as e:
        print(f"ERROR AL INICIAR EL MICROSERVICIO: {e}")