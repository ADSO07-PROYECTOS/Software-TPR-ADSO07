from flask import Flask, render_template, jsonify
from conexion import conectar 

app = Flask(__name__)

@app.route('/api/categorias', methods=['GET'])
def ver_menu():
    lista_categorias = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT menu_id, categoria, imagen FROM menu")
            result = cursor.fetchall()
            
            for row in result:
                categoria = {
                    'id': row['menu_id'],
                    'nombre': row['categoria'],
                    'imagen': row['imagen'] # El nombre del archivo ej: "pizza.jpg"
                }
                lista_categorias.append(categoria)
            
            cursor.close()
            conn.close()

        return jsonify(lista_categorias)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



#Platos

@app.route('/api/platos/<int:categoria_id>', methods=['GET'])
def ver_platos(categoria_id):
    lista_platos = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT p.plato_id, p.nombre AS plato_nombre, p.descripcion, p.precio, p.imagen
                FROM platos p
                JOIN menu m ON p.categoria_id = m.menu_id
                WHERE m.menu_id = %s
            """
            cursor.execute(query, (categoria_id,))
            result = cursor.fetchall()
            
            for row in result:
                plato = {
                    'id': row['plato_id'],
                    'nombre': row['plato_nombre'],
                    'descripcion': row['descripcion'],
                    'precio': float(row['precio']),
                    'imagen': row['imagen'] # El nombre del archivo ej: "platillo.jpg"
                }
                lista_platos.append(plato)
            
            cursor.close()
            conn.close()

        return jsonify(lista_platos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500











if __name__ == '__main__':
    print("--INICIANDO MICROSERVICIO DE MENU EN EL PUERTO 5001 --")
    app.run(debug=True, port=5001, host='0.0.0.0')