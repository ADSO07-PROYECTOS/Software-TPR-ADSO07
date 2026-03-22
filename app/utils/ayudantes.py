"""
Funciones auxiliares reutilizables.
"""
from utils.constantes import ROLES_VALIDOS


def archivo_permitido(nombre_archivo, extensiones_permitidas):
    """Valida que la extensión del archivo esté en el conjunto permitido."""
    return '.' in nombre_archivo and \
        nombre_archivo.rsplit('.', 1)[1].lower() in extensiones_permitidas


def normalizar_rol(valor, predeterminado='cliente'):
    """Normaliza un string de rol; devuelve el predeterminado si no es válido."""
    rol = (valor or predeterminado).strip().lower()
    return rol if rol in ROLES_VALIDOS else predeterminado
