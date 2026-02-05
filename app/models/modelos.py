from conexion import conectar

class Categoria:
    # 1. Agregamos id, nombre e imagen dentro de los paréntesis para recibirlos
    def __init__(self, id, nombre, imagen):
        self.id = id
        self.nombre = nombre
        self.imagen = imagen

    @staticmethod
    def obtener_todas():
        """Traer Categorias de la base de datos"""
        categorias = []
        try:
            conn = conectar()
            if conn:
    
                cursor = conn.cursor(dictionary=True)
                
                # Consulta a la base de datos
                cursor.execute("SELECT menu_id, categoria, imagen FROM menu")
                result = cursor.fetchall()
                
                for row in result:
                    # 3. Creamos el objeto usando los nombres exactos de tus columnas en la BD
                    # Asegúrate de que row['menu_id'] coincida con tu base de datos
                    nueva_categoria = Categoria(
                        id=row['menu_id'], 
                        nombre=row['categoria'], 
                        imagen=row['imagen']
                    )
                    categorias.append(nueva_categoria)
                
                cursor.close()
                conn.close()
        except Exception as e:
            print(f"Error al obtener las categorias: {e}")
        return categorias