from datetime import datetime
from conexion import obtener_conexion

class usuario:
      def login(self, cc_usuario, contrasena):
            sql = "SELECT cc_usuario, rol FROM usuarios WHERE cc_usuario = %s AND nombres = %s"
            conn = obtener_conexion()
            if not conn:
                return None
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cc_usuario, contrasena))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado
      
mi_usuario = usuario()