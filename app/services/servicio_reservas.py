"""
Servicio – Lógica de negocio para reservas del cliente.
"""
import qrcode
import io
import base64

from models.modelo_reserva import (
    obtener_reservas_por_cedula,
    obtener_pedido_reserva,
)
from utils.constantes import DIAS_ES, MESES_ES, URL_SERVIDOR_PUBLICO


def consultar_reservas_cliente(cedula):
    """
    Obtiene las reservas de un cliente, formatea fechas y genera QR para cada una.
    Devuelve (lista_reservas, sin_resultados).
    """
    reservas = obtener_reservas_por_cedula(cedula)

    for reserva in reservas:
        fecha_hora = reserva['fecha_hora']
        if fecha_hora:
            reserva['fecha_formato'] = (
                f"{DIAS_ES[fecha_hora.weekday()]}, {fecha_hora.day} "
                f"{MESES_ES[fecha_hora.month - 1]}, "
                f"{fecha_hora.strftime('%I:%M %p')}"
            )
        else:
            reserva['fecha_formato'] = ''

        reserva['pedido'] = obtener_pedido_reserva(reserva['reserva_id'])

        url_qr = f"{URL_SERVIDOR_PUBLICO}/resumen/reserva/{reserva['reserva_id']}"
        imagen_qr = qrcode.make(url_qr)
        buffer = io.BytesIO()
        imagen_qr.save(buffer, format="PNG")
        reserva['qr_b64'] = base64.b64encode(buffer.getvalue()).decode()

    sin_resultados = len(reservas) == 0
    return reservas, sin_resultados
