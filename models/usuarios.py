from conexion import *

class Usuario:
    def login (self, id,contrasena):
        cifrada = hashlib.sha256(contrasena.encode("utf-8")).hexdigest()
        sql =f"SELECT * FROM usuarios WHERE idusuario='{id}' AND contrasena='{cifrada}'"
        mi_cursor.execute(sql)
        resultado = mi_cursor.fetchone()
        if resultado:
            return True
        return False
    



mi_usuarios =Usuario()