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

            cursor.execute("SELECT categoria_id, nombre_categoria, imagen FROM categoria")
            result = cursor.fetchall()
            
            for row in result:
                categoria = {
                    'id': row['categoria_id'],
                    'nombre': row['nombre_categoria'],
                    'imagen': row['imagen'] # El nombre del archivo ej: "pizza.jpg"
                }
                lista_categorias.append(categoria)
            
            cursor.close()
            conn.close()

        return jsonify(lista_categorias)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    print("--INICIANDO MICROSERVICIO DE MENU EN EL PUERTO 5001 --")
    app.run(debug=True, port=5001, host='0.0.0.0')