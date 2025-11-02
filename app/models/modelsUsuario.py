from datetime import datetime
from conexion import obtener_conexion

class usuario:
      def login(self, cc_usuario, nUsuario):
            sql = "SELECT cc_usuario, rol, nombres, estado FROM usuarios WHERE cc_usuario = %s AND nombres = %s"
            conn = obtener_conexion()
            if not conn:
                return None
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, (cc_usuario, nUsuario))
            resultado = cursor.fetchone()
            cursor.close()
            conn.close()
            return resultado
      
mi_usuario = usuario()