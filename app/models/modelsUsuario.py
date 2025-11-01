from datetime import datetime
from conexion import obtener_conexion


class usuario:
    """
    Clase que representa un usuario del sistema y gestiona su autenticación.
    Methods:
        login(cc_usuario: str, contrasena: str) -> dict | None:
            Autentica un usuario verificando sus credenciales en la base de datos.
            Args:
                cc_usuario (str): Cédula de ciudadanía del usuario a autenticar.
                contrasena (str): Contraseña en texto plano del usuario.
            Returns:
                dict: Diccionario con las claves 'cc_usuario' y 'rol' si la autenticación
                      es exitosa.
                None: Si el usuario no existe, la contraseña es incorrecta o hay error
                      en la conexión a la base de datos.
            Raises:
                Ninguna excepción es lanzada explícitamente. Los errores se registran
                en consola mediante print().
            Notas:
                - La verificación de contraseña se realiza en Python comparando strings.
                - La conexión a la base de datos se cierra al finalizar.
                - Se registran mensajes de depuración en consola con prefijo [LOGIN].
    """

    def login(self, cc_usuario, contrasena):
        sql = "SELECT cc_usuario, rol, contrasena FROM usuarios WHERE cc_usuario = %s"
        conn = obtener_conexion()
        if not conn:
            print(f"[LOGIN] Error: No hay conexión a BD")
            return None
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, (cc_usuario,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()

        print(f"[LOGIN] cc_usuario: {cc_usuario}, resultado: {resultado}")

        if resultado is None:
            print(f"[LOGIN] Usuario no encontrado")
            return None

        # Comparar la contraseña en Python
        if resultado["contrasena"] == contrasena:
            print(f"[LOGIN] Contraseña correcta para {cc_usuario}")
            # Devolver solo cc_usuario y rol (sin la contraseña)
            return {"cc_usuario": resultado["cc_usuario"], "rol": resultado["rol"]}
        else:
            print(f"[LOGIN] Contraseña incorrecta para {cc_usuario}")
            return None


mi_usuario = usuario()
