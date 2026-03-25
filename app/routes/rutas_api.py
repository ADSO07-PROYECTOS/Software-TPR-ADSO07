"""
Blueprint – Rutas de la API (comprobantes, proxy de temáticas, domicilios, plato).
"""
from flask import Blueprint, request, jsonify
import requests

from conexion import conectar
from utils.constantes import (
    URL_MICROSERVICIO_RESERVAS,
    URL_MICROSERVICIO_DOMICILIOS,
    URL_MICROSERVICIO_MENU,
)
from services.servicio_comprobantes import (
    procesar_comprobante_reserva,
    procesar_comprobante_domicilio,
)

bp_api = Blueprint('api', __name__)


# ─── Temáticas (proxy con fallback a BD local) ──────────────────────

@bp_api.route('/api/tematicas', methods=['GET'])
def proxy_tematicas():
    errores = []

    try:
        respuesta = requests.get(f'{URL_MICROSERVICIO_RESERVAS}/api/tematicas', timeout=8)
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        errores.append(f'localhost: {error}')

    try:
        respuesta = requests.get('http://54.156.114.70:5005/api/tematicas', timeout=8)
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        errores.append(f'remoto: {error}')

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
            datos = cursor.fetchall()
        except Exception:
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
            datos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(datos), 200
    except Exception as error:
        errores.append(f'bd: {error}')
        return jsonify({"error": "No fue posible cargar temáticas", "detalles": errores}), 500


# ─── Reservas (proxy) ───────────────────────────────────────────────

@bp_api.route('/api/reservas', methods=['POST'])
def proxy_reservas():
    try:
        respuesta = requests.post(
            'http://54.156.114.70:5005/api/reservas',
            json=request.json, timeout=30
        )
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        return jsonify({"error": str(error)}), 500


# ─── Comprobante de reserva ─────────────────────────────────────────

@bp_api.route('/api/reservas/comprobante', methods=['POST'])
def subir_comprobante_reserva():
    try:
        id_reserva = request.form.get('reserva_id')
        archivo = request.files.get('archivo')
        exito, mensaje, codigo = procesar_comprobante_reserva(id_reserva, archivo)
        return jsonify({'success': exito, 'message': mensaje}), codigo
    except Exception as error:
        return jsonify({'success': False, 'message': str(error)}), 500


# ─── Domicilios (proxy) ─────────────────────────────────────────────

@bp_api.route('/api/domicilios', methods=['POST'])
def proxy_crear_domicilio():
    try:
        respuesta = requests.post(
            f'{URL_MICROSERVICIO_DOMICILIOS}/api/domicilios',
            json=request.get_json(), timeout=30
        )
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        return jsonify({"status": "error", "message": str(error)}), 502


# ─── Comprobante de domicilio ───────────────────────────────────────

@bp_api.route('/api/domicilios/comprobante', methods=['POST'])
def api_subir_comprobante_domicilio():
    try:
        id_domicilio = request.form.get('domicilio_id')
        archivo = request.files.get('archivo')
        exito, mensaje, codigo = procesar_comprobante_domicilio(id_domicilio, archivo)
        return jsonify({'success': exito, 'message': mensaje}), codigo
    except Exception as error:
        return jsonify({'success': False, 'message': str(error)}), 500


# ─── Detalle de plato (proxy) ───────────────────────────────────────

@bp_api.route('/api/plato/<int:id_plato>', methods=['GET'])
def proxy_plato_detalle(id_plato):
    try:
        respuesta = requests.get(f'{URL_MICROSERVICIO_MENU}/api/plato/{id_plato}', timeout=10)
        return jsonify(respuesta.json()), respuesta.status_code
    except Exception as error:
        return jsonify({"error": str(error)}), 502
