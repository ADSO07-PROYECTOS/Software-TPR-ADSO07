import requests
from flask import jsonify


def reenviar_peticion(metodo, url_base, ruta, **kwargs):
    """Reenvía una petición HTTP al microservicio indicado."""
    try:
        respuesta = requests.request(metodo, f'{url_base}{ruta}', timeout=15, **kwargs)
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        return jsonify({"error": str(error)}), 502
