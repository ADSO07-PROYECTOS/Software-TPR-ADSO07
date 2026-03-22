"""
Blueprint – Rutas del panel de administración y proxy al microservicio admin.
"""
import os
from flask import Blueprint, render_template, request, redirect, session, jsonify
from werkzeug.utils import secure_filename
import requests

from utils.constantes import URL_MICROSERVICIO_ADMIN, CARPETA_IMAGENES, EXTENSIONES_IMAGEN
from utils.ayudantes import archivo_permitido, normalizar_rol
from services.servicio_proxy import reenviar_peticion

bp_admin = Blueprint('admin', __name__)


# ─── Panel principal ─────────────────────────────────────────────────

@bp_admin.route('/admin')
def panel_admin():
    rol = session.get('rol')
    if rol not in ('administrador', 'cajero'):
        return redirect('/login')

    estadisticas = {
        'domicilios_hoy': 0, 'domicilios_pendientes': 0,
        'mesas_disponibles': 0, 'mesas_ocupadas': 0, 'mesas_reservadas': 0,
    }
    mesas_por_piso = []
    pedidos_recientes = []

    try:
        respuesta = requests.get(f'{URL_MICROSERVICIO_ADMIN}/api/admin/stats', timeout=10)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            estadisticas = datos.get('stats', estadisticas)
            mesas_por_piso = datos.get('mesas_por_piso', [])
            pedidos_recientes = datos.get('pedidos_recientes', [])
    except Exception as error:
        print(f"Error contactando microservicio admin: {error}")

    return render_template('admin/panel.html',
                           stats=estadisticas,
                           mesas_por_piso=mesas_por_piso,
                           pedidos_recientes=pedidos_recientes,
                           rol_usuario=rol,
                           nombre_usuario=session.get('usuario_nombre', ''))


# ─── Helper de proxy ─────────────────────────────────────────────────

def _proxy(metodo, ruta, **kwargs):
    return reenviar_peticion(metodo, URL_MICROSERVICIO_ADMIN, ruta, **kwargs)


# ─── Clientes ────────────────────────────────────────────────────────

@bp_admin.route('/admin/api/clientes', methods=['GET'])
def admin_clientes():
    return _proxy('GET', '/api/admin/clientes')


@bp_admin.route('/admin/api/clientes', methods=['POST'])
def admin_clientes_post():
    datos = request.get_json() or {}
    datos['rol'] = normalizar_rol(datos.get('rol'))
    return _proxy('POST', '/api/admin/clientes', json=datos)


@bp_admin.route('/admin/api/clientes/<int:id_cliente>', methods=['PUT'])
def admin_cliente_put(id_cliente):
    datos = request.get_json() or {}
    datos['rol'] = normalizar_rol(datos.get('rol'))
    return _proxy('PUT', f'/api/admin/clientes/{id_cliente}', json=datos)


@bp_admin.route('/admin/api/clientes/<int:id_cliente>', methods=['DELETE'])
def admin_cliente_delete(id_cliente):
    return _proxy('DELETE', f'/api/admin/clientes/{id_cliente}')


# ─── Productos ───────────────────────────────────────────────────────

@bp_admin.route('/admin/api/productos', methods=['GET'])
def admin_productos_get():
    return _proxy('GET', '/api/admin/productos')


@bp_admin.route('/admin/api/productos', methods=['POST'])
def admin_productos_post():
    return _proxy('POST', '/api/admin/productos', json=request.get_json())


@bp_admin.route('/admin/api/productos/<int:id_producto>', methods=['PUT'])
def admin_producto_put(id_producto):
    return _proxy('PUT', f'/api/admin/productos/{id_producto}', json=request.get_json())


@bp_admin.route('/admin/api/productos/<int:id_producto>', methods=['DELETE'])
def admin_producto_delete(id_producto):
    return _proxy('DELETE', f'/api/admin/productos/{id_producto}')


# ─── Categorías ──────────────────────────────────────────────────────

@bp_admin.route('/admin/api/categorias', methods=['GET'])
def admin_categorias_get():
    return _proxy('GET', '/api/admin/categorias')


@bp_admin.route('/admin/api/categorias', methods=['POST'])
def admin_categorias_post():
    return _proxy('POST', '/api/admin/categorias', json=request.get_json())


@bp_admin.route('/admin/api/categorias/<int:id_categoria>', methods=['PUT'])
def admin_categorias_put(id_categoria):
    return _proxy('PUT', f'/api/admin/categorias/{id_categoria}', json=request.get_json())


# ─── Domicilios ──────────────────────────────────────────────────────

@bp_admin.route('/admin/api/domicilios', methods=['GET'])
def admin_domicilios_get():
    return _proxy('GET', '/api/admin/domicilios')


@bp_admin.route('/admin/api/domicilios/<int:id_domicilio>', methods=['PUT'])
def admin_domicilio_put(id_domicilio):
    return _proxy('PUT', f'/api/admin/domicilios/{id_domicilio}', json=request.get_json())


# ─── Reservas ────────────────────────────────────────────────────────

@bp_admin.route('/admin/api/reservas', methods=['GET'])
def admin_reservas_get():
    return _proxy('GET', '/api/admin/reservas')


@bp_admin.route('/admin/api/reservas/<int:id_reserva>', methods=['PUT'])
def admin_reserva_put(id_reserva):
    return _proxy('PUT', f'/api/admin/reservas/{id_reserva}', json=request.get_json())


# ─── Temáticas ───────────────────────────────────────────────────────

@bp_admin.route('/admin/api/tematicas', methods=['GET'])
def admin_tematicas_get():
    return _proxy('GET', '/api/admin/tematicas')


@bp_admin.route('/admin/api/tematicas', methods=['POST'])
def admin_tematicas_post():
    return _proxy('POST', '/api/admin/tematicas', json=request.get_json())


@bp_admin.route('/admin/api/tematicas/<int:id_tematica>', methods=['DELETE'])
def admin_tematica_delete(id_tematica):
    return _proxy('DELETE', f'/api/admin/tematicas/{id_tematica}')


@bp_admin.route('/admin/api/tematicas/<int:id_tematica>', methods=['PUT'])
def admin_tematicas_put(id_tematica):
    return _proxy('PUT', f'/api/admin/tematicas/{id_tematica}', json=request.get_json())


# ─── Mesas ───────────────────────────────────────────────────────────

@bp_admin.route('/admin/api/mesas', methods=['GET'])
def admin_mesas_get():
    return _proxy('GET', '/api/admin/mesas')


@bp_admin.route('/admin/api/mesas', methods=['POST'])
def admin_mesas_post():
    return _proxy('POST', '/api/admin/mesas', json=request.get_json())


@bp_admin.route('/admin/api/mesas/<int:id_mesa>', methods=['PUT'])
def admin_mesa_put(id_mesa):
    return _proxy('PUT', f'/api/admin/mesas/{id_mesa}', json=request.get_json())


@bp_admin.route('/admin/api/mesas/<int:id_mesa>', methods=['DELETE'])
def admin_mesa_delete(id_mesa):
    return _proxy('DELETE', f'/api/admin/mesas/{id_mesa}')


# ─── Usuarios ────────────────────────────────────────────────────────

@bp_admin.route('/admin/api/usuarios', methods=['GET'])
def admin_usuarios_get():
    return _proxy('GET', '/api/admin/usuarios')


@bp_admin.route('/admin/api/usuarios', methods=['POST'])
def admin_usuarios_post():
    return _proxy('POST', '/api/admin/usuarios', json=request.get_json())


@bp_admin.route('/admin/api/usuarios/<int:id_usuario>', methods=['PUT'])
def admin_usuario_put(id_usuario):
    return _proxy('PUT', f'/api/admin/usuarios/{id_usuario}', json=request.get_json())


@bp_admin.route('/admin/api/usuarios/<int:id_usuario>', methods=['DELETE'])
def admin_usuario_delete(id_usuario):
    return _proxy('DELETE', f'/api/admin/usuarios/{id_usuario}')


# ─── Subida de imagen de producto ────────────────────────────────────

@bp_admin.route('/admin/api/upload-imagen', methods=['POST'])
def admin_upload_imagen():
    try:
        if 'imagen' not in request.files:
            return jsonify({'error': 'No se envió ningún archivo'}), 400
        archivo = request.files['imagen']
        if archivo.filename == '':
            return jsonify({'error': 'Nombre de archivo vacío'}), 400
        if not archivo_permitido(archivo.filename, EXTENSIONES_IMAGEN):
            return jsonify({'error': 'Formato no permitido. Usa PNG, JPG o WEBP'}), 400

        nombre = secure_filename(archivo.filename)
        ruta = os.path.join(CARPETA_IMAGENES, nombre)
        archivo.save(ruta)
        return jsonify({'url': f'platos/{nombre}'})
    except Exception as error:
        return jsonify({'error': 'Error interno al guardar la imagen', 'detalle': str(error)}), 500
