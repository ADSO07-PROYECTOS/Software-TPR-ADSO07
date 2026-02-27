from flask import Flask, render_template, jsonify
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

            cursor.execute("SELECT categoria_id, nombre_categoria, imagen_categoria FROM categorias")
            result = cursor.fetchall()
            
            for row in result:
                categoria = {
                    'id': row['categoria_id'],
                    'nombre': row['nombre_categoria'],
                    'imagen': row['imagen_categoria'] 
                }
                lista_categorias.append(categoria)
            
            cursor.close()
            conn.close()

        return jsonify(lista_categorias)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/api/platos/<int:id_categoria>', methods=['GET'])
def ver_platos_por_categoria(id_categoria):
    lista_platos = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Asegúrate de que los nombres de columnas coincidan con tu tabla 'menu'
            query = "SELECT * FROM menu WHERE categoria_id = %s"
            cursor.execute(query, (id_categoria,))
            result = cursor.fetchall()
            
            for row in result:
                plato = {
                    'id': row.get('menu_id'), 
                    'nombre': row.get('nombre_plato'),
                    'precio': row.get('precio_plato'),
                    'descripcion': row.get('descripcion'),
                    'imagen': row.get('imagen'),
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
            query = "SELECT * FROM menu WHERE menu_id = %s"
            cursor.execute(query, (id_plato,))
            row = cursor.fetchone() # Usamos fetchone porque solo queremos uno
            
            cursor.close()
            conn.close()

            if row:
                plato = {
                    'id': row.get('menu_id'), 
                    'nombre': row.get('nombre_plato'),
                    'precio': row.get('precio_plato'),
                    'descripcion': row.get('descripcion'),
                    'imagen': row.get('imagen'),
                    'categoria_id': row.get('categoria_id')
                }
                return jsonify(plato)
            else:
                return jsonify({"error": "Plato no encontrado"}), 404

    except Exception as e:
        print(f"Error buscando plato: {e}")
        return jsonify({"error": str(e)}), 500

        # ... importaciones y rutas anteriores ...

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
            
            # 1. Obtener Tamaños
            cursor.execute("SELECT * FROM tamanos_pizza ORDER BY precio ASC")
            datos["tamanos"] = cursor.fetchall()

            # 2. Obtener Adiciones
            cursor.execute("SELECT * FROM adiciones")
            datos["adiciones"] = cursor.fetchall()

            # 3. Obtener Sabores
            cursor.execute("SELECT * FROM sabores")
            datos["sabores"] = cursor.fetchall()
            
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