from flask import Flask, jsonify
from conexion import conectar

app = Flask(__name__)

@app.route('/categorias', methods=['GET'])
def obtener_categorias():
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
                    'imagen': row['imagen']
                }
                lista_categorias.append(categoria)
            cursor.close()
            conn.close()
            return jsonify(lista_categorias)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("--INICIANDO MICROSERVICIO DE MENU EN EL PUERTO 5001")
    app.run(debug=True, port=5001)
        


    

