
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, jsonify
import requests

from utils.constantes import URL_MICROSERVICIO_MENU, URL_MICROSERVICIO_MIS_RESERVAS
from models.modelo_tematica import obtener_tematicas
from models.modelo_reserva import (
    obtener_reserva_con_tematica,
    obtener_productos_reserva,
)
from models.modelo_domicilio import obtener_domicilio_por_id, obtener_productos_domicilio
from models.modelo_cliente import obtener_cliente_por_id

bp_cliente = Blueprint('cliente', __name__)


# ─── Menú y catálogo ─────────────────────────────────────────────────

@bp_cliente.route('/')
@bp_cliente.route('/menu')
def ver_menu():
    try:
        respuesta = requests.get(f'{URL_MICROSERVICIO_MENU}/api/categorias', timeout=10)
        respuesta.raise_for_status()
        mis_categorias = respuesta.json()
    except Exception as error:
        print(f"Error al obtener categorías: {error}")
        mis_categorias = []
    return render_template('client/menu.html', lista_categorias=mis_categorias)


@bp_cliente.route('/menu/<int:id_categoria>')
def ver_platos(id_categoria):
    mis_platos = []
    try:
        respuesta = requests.get(f'{URL_MICROSERVICIO_MENU}/api/platos/{id_categoria}', timeout=10)
        respuesta.raise_for_status()
        mis_platos = respuesta.json()
    except Exception as error:
        print(f"Error al obtener platos: {error}")
    return render_template('client/ver_platos.html', lista_platos=mis_platos)


@bp_cliente.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    datos_extras = {"tamanos": [], "adiciones": [], "sabores": []}
    try:
        res_plato = requests.get(f'{URL_MICROSERVICIO_MENU}/api/plato/{id_plato}', timeout=5)
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        res_extras = requests.get(f'{URL_MICROSERVICIO_MENU}/api/extras', timeout=5)
        if res_extras.status_code == 200:
            datos_extras = res_extras.json()
    except Exception as error:
        print(f"Error en detalle plato: {error}")

    nombre_categoria = info_plato.get('categoria_nombre', '').lower()
    es_pizza = 'pizza' in nombre_categoria

    return render_template('client/detalle_plato.html',
                           plato=info_plato,
                           es_pizza=es_pizza,
                           tamanos=datos_extras.get('tamanos', []),
                           adiciones=datos_extras.get('adiciones', []),
                           sabores=datos_extras.get('sabores', []))


@bp_cliente.route('/carrito')
def ver_carrito():
    return render_template('client/carrito.html')


# ─── Datos del cliente / domicilio ───────────────────────────────────

@bp_cliente.route('/datos_cliente')
def vista_cliente():
    return render_template('client/detalles_cliente.html')


@bp_cliente.route('/direccion_domicilio')
def vista_domicilio():
    return render_template('client/direccion_domicilio.html')


# ─── Reservas ────────────────────────────────────────────────────────

@bp_cliente.route('/detalles_reserva')
def vista_reserva():
    lista_tematicas = []
    try:
        lista_tematicas = obtener_tematicas()
    except Exception as error:
        print(f"Error al obtener temáticas: {error}")
    return render_template('client/detalles_reserva.html', tematicas=lista_tematicas)


@bp_cliente.route('/exito')
def vista_exito():
    return render_template('client/exito.html')


@bp_cliente.route('/subir_comprobante')
def subir_comprobante():
    return render_template('client/subir_com.html')


@bp_cliente.route('/subir_comprobante_domicilio')
def subir_comprobante_domicilio():
    return render_template('client/subir_com_domicilio.html')


@bp_cliente.route('/resumen/reserva/<int:id_reserva>')
def resumen_reserva(id_reserva):
    try:
        reserva = obtener_reserva_con_tematica(id_reserva)
        if not reserva:
            return "Reserva no encontrada", 404

        cliente = obtener_cliente_por_id(reserva['cliente_id'])
        productos = obtener_productos_reserva(id_reserva)

        return render_template('client/resumen_reserva.html',
                               reserva=reserva,
                               cliente=cliente,
                               productos=productos,
                               tematica=reserva.get('nombre_tematica', 'N/A'))
    except Exception as error:
        return f"Error: {error}", 500


@bp_cliente.route('/resumen/domicilio/<int:id_domicilio>')
def resumen_domicilio(id_domicilio):
    try:
        domicilio = obtener_domicilio_por_id(id_domicilio)
        if not domicilio:
            return "Domicilio no encontrado", 404

        cliente = obtener_cliente_por_id(domicilio['cliente_id'])
        productos = obtener_productos_domicilio(id_domicilio)

        return render_template('client/resumen_domicilio.html',
                               domicilio=domicilio,
                               cliente=cliente,
                               productos=productos)
    except Exception as error:
        return f"Error: {error}", 500


@bp_cliente.route('/mis_reservas')
def mis_reservas():
    cedula = request.args.get('cedula', '').strip()
    reservas = []
    buscado = False
    sin_resultados = False

    if cedula:
        buscado = True
        try:
            resp = requests.get(
                f'{URL_MICROSERVICIO_MIS_RESERVAS}/api/mis_reservas',
                params={'cedula': cedula},
                timeout=15
            )
            if resp.status_code == 200:
                data = resp.json()
                reservas = data.get('reservas', [])
                sin_resultados = data.get('sin_resultados', False)
            else:
                print(f"Error microservicio mis_reservas: {resp.status_code}")
        except Exception as error:
            print(f"Error al obtener reservas: {error}")

    return render_template('client/mis_reservas.html',
                           reservas=reservas,
                           cedula=cedula,
                           buscado=buscado,
                           sin_resultados=sin_resultados)


@bp_cliente.route('/mis_reservas/<int:id_reserva>/eliminar', methods=['POST'])
def eliminar_reserva(id_reserva):
    try:
        resp = requests.delete(
            f'{URL_MICROSERVICIO_MIS_RESERVAS}/api/mis_reservas/{id_reserva}',
            timeout=15
        )
        if resp.status_code == 200:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": resp.json().get('error', 'Error')}), resp.status_code
    except Exception as error:
        return jsonify({"success": False, "message": str(error)}), 500


@bp_cliente.route('/mis_reservas/<int:id_reserva>/modificar', methods=['GET', 'POST'])
def modificar_reserva(id_reserva):
    if request.method == 'POST':
        try:
            datos = request.form
            fecha_hora = f"{datos['fecha']} {datos['hora']}:00:00"
            resp = requests.put(
                f'{URL_MICROSERVICIO_MIS_RESERVAS}/api/mis_reservas/{id_reserva}',
                json={
                    'fecha_hora': fecha_hora,
                    'personas': datos['personas'],
                    'tematica': datos['tematica'],
                    'nombre': datos['nombre'],
                    'email': datos['email'],
                    'telefono': datos['telefono']
                },
                timeout=15
            )
            if resp.status_code != 200:
                return f"Error al modificar: {resp.json().get('error', 'Error')}", 500
            return redirect('/mis_reservas')
        except Exception as error:
            return f"Error al modificar: {error}", 500
    else:
        try:
            resp = requests.get(
                f'{URL_MICROSERVICIO_MIS_RESERVAS}/api/mis_reservas/{id_reserva}',
                timeout=15
            )
            if resp.status_code != 200:
                return redirect('/mis_reservas')
            reserva = resp.json()

            # Convertir fecha_hora string a datetime para el template
            if reserva.get('fecha_hora'):
                reserva['fecha_hora'] = datetime.strptime(reserva['fecha_hora'], '%Y-%m-%d %H:%M:%S')

            tematicas = obtener_tematicas()
            fecha_actual = datetime.today()
            return render_template('client/modificar_reserva.html',
                                   reserva=reserva,
                                   tematicas=tematicas,
                                   fecha_actual=fecha_actual,
                                   timedelta=timedelta)
        except Exception as error:
            return f"Error: {error}", 500
