
import os
from werkzeug.utils import secure_filename

from utils.constantes import CARPETA_COMPROBANTES, EXTENSIONES_COMPROBANTE, MAX_TAMANO_COMPROBANTE
from utils.ayudantes import archivo_permitido
from models.modelo_reserva import obtener_cedula_por_reserva, guardar_comprobante_reserva
from models.modelo_domicilio import obtener_cedula_por_domicilio, guardar_comprobante_domicilio


def procesar_comprobante_reserva(id_reserva, archivo):
   
    if not id_reserva:
        return False, 'ID de reserva no proporcionado', 400
    if not archivo or archivo.filename == '':
        return False, 'No se envió ningún archivo', 400
    if not archivo_permitido(archivo.filename, EXTENSIONES_COMPROBANTE):
        return False, 'Formato no permitido. Usa PNG, JPG o PDF', 400

    archivo.seek(0, 2)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > MAX_TAMANO_COMPROBANTE:
        return False, 'El archivo excede el tamaño máximo permitido (5 MB)', 400

    cedula = obtener_cedula_por_reserva(id_reserva)
    if not cedula:
        return False, f'Reserva #{id_reserva} no encontrada', 404

    extension = archivo.filename.rsplit('.', 1)[1].lower()
    nombre_archivo = secure_filename(f"comprobante_{cedula}.{extension}")
    ruta_completa = os.path.join(CARPETA_COMPROBANTES, nombre_archivo)
    archivo.save(ruta_completa)

    ruta_relativa = f'comprobantes/{nombre_archivo}'
    guardar_comprobante_reserva(id_reserva, ruta_relativa)
    return True, 'Comprobante recibido correctamente', 200


def procesar_comprobante_domicilio(id_domicilio, archivo):

    if not id_domicilio:
        return False, 'ID de pedido no proporcionado', 400
    if not archivo or archivo.filename == '':
        return False, 'No se envió ningún archivo', 400
    if not archivo_permitido(archivo.filename, EXTENSIONES_COMPROBANTE):
        return False, 'Formato no permitido. Usa PNG, JPG o PDF', 400

    archivo.seek(0, 2)
    tamano = archivo.tell()
    archivo.seek(0)
    if tamano > MAX_TAMANO_COMPROBANTE:
        return False, 'El archivo excede el tamaño máximo permitido (5 MB)', 400

    cedula = obtener_cedula_por_domicilio(id_domicilio)
    if not cedula:
        return False, f'Pedido #{id_domicilio} no encontrado', 404

    extension = archivo.filename.rsplit('.', 1)[1].lower()
    nombre_archivo = secure_filename(f"comprobante_dom_{cedula}.{extension}")
    ruta_completa = os.path.join(CARPETA_COMPROBANTES, nombre_archivo)
    archivo.save(ruta_completa)

    ruta_relativa = f'comprobantes/{nombre_archivo}'
    guardar_comprobante_domicilio(id_domicilio, ruta_relativa)
    return True, 'Comprobante recibido correctamente', 200
