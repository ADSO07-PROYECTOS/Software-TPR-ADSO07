from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS
from conexion import conectar
import requests
import qrcode, io, base64
import os

try:
    import flask_monitoringdashboard as dashboard
except ImportError:
    dashboard = None
from werkzeug.utils import secure_filename

# Carpetas de subida
UPLOAD_FOLDER_IMG = os.path.join(os.path.dirname(__file__), 'static', 'img', 'platos')
UPLOAD_FOLDER_COMPROBANTES = os.path.join(os.path.dirname(__file__), 'static', 'comprobantes')
os.makedirs(UPLOAD_FOLDER_IMG, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_COMPROBANTES, exist_ok=True)

ALLOWED_EXT_IMG = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_EXT_COMPROBANTE = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename, allowed_ext):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext

DIAS_ES = ['LUNES','MARTES','MIÉRCOLES','JUEVES','VIERNES','SÁBADO','DOMINGO']
MESES_ES = ['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO',
            'AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']

app = Flask(__name__)
CORS(app)

# Configura Flask-MonitoringDashboard si el paquete está instalado.
if dashboard:
    dashboard_config_path = os.path.join(os.path.dirname(__file__), 'dashboard.cfg')
    if os.path.exists(dashboard_config_path):
        dashboard.config.init_from(file=dashboard_config_path)
    dashboard.bind(app)
else:
    print("Adv: flask-monitoringdashboard no está instalado. Instálalo para habilitar /dashboard.")

ROLES_VALIDOS = {'cliente', 'cajero', 'administrador'}


def normalizar_rol(valor, predeterminado='cliente'):
    rol = (valor or predeterminado).strip().lower()
    return rol if rol in ROLES_VALIDOS else predeterminado


# Migración: asegurar que tabla reservas tiene columna para comprobante
try:
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SHOW COLUMNS FROM reservas LIKE 'comprobante_transferencia'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE reservas ADD COLUMN comprobante_transferencia VARCHAR(255) NULL
            """)
            conn.commit()
            print("✓ Columna 'comprobante_transferencia' agregada a tabla reservas")

        cursor.execute("SHOW COLUMNS FROM clientes LIKE 'rol'")
        if not cursor.fetchone():
            cursor.execute("""
                ALTER TABLE clientes
                ADD COLUMN rol VARCHAR(20) NOT NULL DEFAULT 'cliente'
            """)
            conn.commit()
            print("✓ Columna 'rol' agregada a tabla clientes")

        cursor.execute("""
            UPDATE clientes
            SET rol = 'cliente'
            WHERE rol IS NULL OR TRIM(rol) = ''
        """)
        conn.commit()
        cursor.close()
        conn.close()
except Exception as e:
    print(f"Adv: No se pudo verificar migraciones iniciales: {e}")


@app.route('/')
def inicio():
    return ver_menu()

@app.route('/menu')
def ver_menu():
    try:
        respuesta = requests.get('http://localhost:5001/api/categorias', timeout=10)
        respuesta.raise_for_status()
        mis_categorias = respuesta.json()
    except Exception as e:
        print(f"Error al obtener categorías: {e}")
        mis_categorias = [] 
    return render_template('client/menu.html', lista_categorias=mis_categorias)

@app.route('/datos_cliente')
def vista_cliente():
    return render_template('client/detalles_cliente.html')

@app.route('/direccion_domicilio')
def vista_domicilio():
    return render_template('client/direccion_domicilio.html')
    
@app.route('/detalles_reserva')
def vista_reserva():
    lista_tematicas = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
                lista_tematicas = cursor.fetchall()
            except Exception:
                # Compatibilidad con instalaciones antiguas donde la tabla era singular.
                cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
                lista_tematicas = cursor.fetchall()
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error al obtener temáticas: {e}")

    return render_template('client/detalles_reserva.html', tematicas=lista_tematicas)

@app.route('/exito')
def vista_exito():
    return render_template('client/exito.html')

@app.route('/subir_comprobante')
def subir_comprobante():
    return render_template('client/subir_com.html')

@app.route('/resumen/reserva/<int:id_reserva>')
def resumen_reserva(id_reserva):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT r.*, t.nombre_tematica
            FROM reservas r
            LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
            WHERE r.reserva_id = %s
        """, (id_reserva,))
        reserva = cursor.fetchone()
        if not reserva:
            return "Reserva no encontrada", 404

        cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (reserva['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("""
            SELECT dr.cantidad, dr.valor_unitario, p.nombre_producto
            FROM detalles_reservas dr
            JOIN productos p ON dr.producto_id = p.producto_id
            WHERE dr.reserva_id = %s
        """, (id_reserva,))
        productos = cursor.fetchall()

        cursor.close(); conn.close()
        return render_template('client/resumen_reserva.html',
                               reserva=reserva,
                               cliente=cliente,
                               productos=productos,
                               tematica=reserva.get('nombre_tematica', 'N/A'))
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/resumen/domicilio/<int:id_domicilio>')
def resumen_domicilio(id_domicilio):
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM domicilios WHERE domicilio_id = %s", (id_domicilio,))
        domicilio = cursor.fetchone()
        if not domicilio:
            return "Domicilio no encontrado", 404

        cursor.execute("SELECT * FROM clientes WHERE cliente_id = %s", (domicilio['cliente_id'],))
        cliente = cursor.fetchone()

        cursor.execute("""
            SELECT dd.cantidad, dd.valor_unitario, p.nombre_producto
            FROM detalles_domicilios dd
            JOIN productos p ON dd.producto_id = p.producto_id
            WHERE dd.domicilio_id = %s
        """, (id_domicilio,))
        productos = cursor.fetchall()

        cursor.close(); conn.close()
        return render_template('client/resumen_domicilio.html',
                               domicilio=domicilio,
                               cliente=cliente,
                               productos=productos)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/carrito')
def ver_carrito():
    return render_template('client/carrito.html')


@app.route('/menu/<int:id_categoria>')
def ver_platos(id_categoria):
    mis_platos = []
    try:
        url_microservicio = f'http://localhost:5001/api/platos/{id_categoria}'
        respuesta = requests.get(url_microservicio, timeout=10)
        respuesta.raise_for_status()
        mis_platos = respuesta.json()
    except Exception as e:
        print(f"Error al obtener platos: {e}")
    return render_template('client/ver_platos.html', lista_platos=mis_platos)

@app.route('/detalle/<int:id_plato>')
def detalle_plato(id_plato):
    info_plato = {}
    datos_extras = {"tamanos": [], "adiciones": [], "sabores": []}
    try:
        res_plato = requests.get(f'http://localhost:5001/api/plato/{id_plato}', timeout=5)
        if res_plato.status_code == 200:
            info_plato = res_plato.json()

        res_extras = requests.get('http://localhost:5001/api/extras', timeout=5)
        if res_extras.status_code == 200:
            datos_extras = res_extras.json()
    except Exception as e:
        print(f"Error en detalle plato: {e}")

    categoria_nombre = info_plato.get('categoria_nombre', '').lower()
    es_pizza = 'pizza' in categoria_nombre

    return render_template('client/detalle_plato.html', 
                           plato=info_plato,
                           es_pizza=es_pizza,
                           tamanos=datos_extras.get('tamanos', []),
                           adiciones=datos_extras.get('adiciones', []),
                           sabores=datos_extras.get('sabores', []))

@app.route('/mis_reservas')
def mis_reservas():
    cedula = request.args.get('cedula', '').strip()
    reservas = []
    buscado = False
    sin_resultados = False
    if cedula:
        buscado = True
        try:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.estado,
                       c.nombre, c.email, c.telefono, c.cc_cliente,
                       t.nombre_tematica, m.piso
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.cliente_id
                LEFT JOIN tematicas t ON r.tematica_id = t.tematica_id
                LEFT JOIN mesas m ON r.mesa_id = m.mesa_id
                WHERE c.cc_cliente = %s
                ORDER BY r.fecha_hora DESC
            """, (cedula,))
            reservas = cursor.fetchall()

            for res in reservas:
                # Formatear fecha en español
                fh = res['fecha_hora']
                if fh:
                    res['fecha_formato'] = (
                        f"{DIAS_ES[fh.weekday()]}, {fh.day} "
                        f"{MESES_ES[fh.month - 1]}, "
                        f"{fh.strftime('%I:%M %p')}"
                    )
                else:
                    res['fecha_formato'] = ''

                # Traer productos del pedido
                cursor.execute("""
                    SELECT p.nombre_producto, dr.cantidad, dr.notas
                    FROM detalles_reservas dr
                    JOIN productos p ON dr.producto_id = p.producto_id
                    WHERE dr.reserva_id = %s
                """, (res['reserva_id'],))
                res['pedido'] = cursor.fetchall()

                # Generar QR como base64
                url_qr = f"http://147.182.238.195:5000/resumen/reserva/{res['reserva_id']}"
                qr_img = qrcode.make(url_qr)
                buf = io.BytesIO()
                qr_img.save(buf, format="PNG")
                res['qr_b64'] = base64.b64encode(buf.getvalue()).decode()

            cursor.close()
            conn.close()
            if not reservas:
                sin_resultados = True
        except Exception as e:
            print(f"Error al obtener reservas: {e}")
    return render_template('client/mis_reservas.html', reservas=reservas,
                           cedula=cedula, buscado=buscado, sin_resultados=sin_resultados)


@app.route('/mis_reservas/<int:id_reserva>/eliminar', methods=['POST'])
def eliminar_reserva(id_reserva):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM detalles_reservas WHERE reserva_id = %s", (id_reserva,))
        cursor.execute("DELETE FROM reservas WHERE reserva_id = %s", (id_reserva,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/mis_reservas/<int:id_reserva>/modificar', methods=['GET', 'POST'])
def modificar_reserva(id_reserva):
    if request.method == 'POST':
        try:
            datos = request.form
            conn = conectar()
            cursor = conn.cursor()
            fecha_hora = f"{datos['fecha']} {datos['hora']}:00:00"
            cursor.execute("""
                UPDATE reservas
                SET fecha_hora = %s, cantidad_personas = %s, tematica_id = %s
                WHERE reserva_id = %s
            """, (fecha_hora, datos['personas'], datos['tematica'], id_reserva))
            cursor.execute("""
                UPDATE clientes c
                JOIN reservas r ON r.cliente_id = c.cliente_id
                SET c.nombre = %s, c.email = %s, c.telefono = %s
                WHERE r.reserva_id = %s
            """, (datos['nombre'], datos['email'], datos['telefono'], id_reserva))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/mis_reservas')
        except Exception as e:
            return f"Error al modificar: {e}", 500
    else:
        try:
            conn = conectar()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.tematica_id, r.estado,
                       c.nombre, c.email, c.telefono, c.cc_cliente
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.cliente_id
                WHERE r.reserva_id = %s
            """, (id_reserva,))
            reserva = cursor.fetchone()
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
            tematicas = cursor.fetchall()
            cursor.close()
            conn.close()
            if not reserva:
                return redirect('/mis_reservas')
            return render_template('client/modificar_reserva.html', reserva=reserva, tematicas=tematicas)
        except Exception as e:
            return f"Error: {e}", 500


@app.route('/api/tematicas', methods=['GET'])
def proxy_tematicas():
    errores = []

    # 1) Intentar primero con microservicio local.
    try:
        resp = requests.get('http://localhost:5005/api/tematicas', timeout=8)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        errores.append(f'localhost: {e}')

    # 2) Fallback al host desplegado.
    try:
        resp = requests.get('http://147.182.238.195:5005/api/tematicas', timeout=8)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        errores.append(f'remoto: {e}')

    # 3) Fallback final a BD local para no romper la vista.
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
            data = cursor.fetchall()
        except Exception:
            cursor.execute("SELECT tematica_id, nombre_tematica FROM tematica")
            data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(data), 200
    except Exception as e:
        errores.append(f'bd: {e}')
        return jsonify({"error": "No fue posible cargar temáticas", "detalles": errores}), 500

@app.route('/api/reservas', methods=['POST'])
def proxy_reservas():
    try:
        resp = requests.post('http://147.182.238.195:5005/api/reservas',
                             json=request.json, timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─────────────────────────── PANEL ADMINISTRACIÓN ────────────────────────────
# Toda la lógica de datos vive en el microservicio admin (puerto 5006).
# app.py solo renderiza la vista y reenvía las llamadas de la API.

ADMIN_MS = 'http://localhost:5006'

@app.route('/admin')
def panel_admin():
    stats           = {'domicilios_hoy': 0, 'domicilios_pendientes': 0,
                       'mesas_disponibles': 0, 'mesas_ocupadas': 0, 'mesas_reservadas': 0}
    mesas_por_piso  = []
    pedidos_recientes = []
    try:
        resp = requests.get(f'{ADMIN_MS}/api/admin/stats', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            stats             = data.get('stats', stats)
            mesas_por_piso    = data.get('mesas_por_piso', [])
            pedidos_recientes = data.get('pedidos_recientes', [])
    except Exception as e:
        print(f"Error contactando microservicio admin: {e}")

    return render_template('admin/panel.html',
                           stats=stats,
                           mesas_por_piso=mesas_por_piso,
                           pedidos_recientes=pedidos_recientes)


def _proxy_admin(metodo, ruta, **kwargs):
    """Reenvía una petición al microservicio admin y devuelve su respuesta."""
    try:
        resp = requests.request(metodo, f'{ADMIN_MS}{ruta}', timeout=15, **kwargs)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502


# Clientes
@app.route('/admin/api/clientes', methods=['GET'])
def admin_clientes():
    return _proxy_admin('GET', '/api/admin/clientes')

@app.route('/admin/api/clientes', methods=['POST'])
def admin_clientes_post():
    datos = request.get_json() or {}
    datos['rol'] = normalizar_rol(datos.get('rol'))
    return _proxy_admin('POST', '/api/admin/clientes', json=datos)

@app.route('/admin/api/clientes/<int:cid>', methods=['PUT'])
def admin_cliente_put(cid):
    datos = request.get_json() or {}
    datos['rol'] = normalizar_rol(datos.get('rol'))
    return _proxy_admin('PUT', f'/api/admin/clientes/{cid}', json=datos)

@app.route('/admin/api/clientes/<int:cid>', methods=['DELETE'])
def admin_cliente_delete(cid):
    return _proxy_admin('DELETE', f'/api/admin/clientes/{cid}')

# Productos
@app.route('/admin/api/productos', methods=['GET'])
def admin_productos_get():
    return _proxy_admin('GET', '/api/admin/productos')

@app.route('/admin/api/productos', methods=['POST'])
def admin_productos_post():
    return _proxy_admin('POST', '/api/admin/productos', json=request.get_json())

@app.route('/admin/api/productos/<int:pid>', methods=['PUT'])
def admin_producto_put(pid):
    return _proxy_admin('PUT', f'/api/admin/productos/{pid}', json=request.get_json())

@app.route('/admin/api/productos/<int:pid>', methods=['DELETE'])
def admin_producto_delete(pid):
    return _proxy_admin('DELETE', f'/api/admin/productos/{pid}')

@app.route('/admin/api/categorias', methods=['GET'])
def admin_categorias_get():
    return _proxy_admin('GET', '/api/admin/categorias')

@app.route('/admin/api/categorias', methods=['POST'])
def admin_categorias_post():
    return _proxy_admin('POST', '/api/admin/categorias', json=request.get_json())

# Domicilios
@app.route('/admin/api/domicilios', methods=['GET'])
def admin_domicilios_get():
    return _proxy_admin('GET', '/api/admin/domicilios')

@app.route('/admin/api/domicilios/<int:did>', methods=['PUT'])
def admin_domicilio_put(did):
    return _proxy_admin('PUT', f'/api/admin/domicilios/{did}', json=request.get_json())

# Reservas
@app.route('/admin/api/reservas', methods=['GET'])
def admin_reservas_get():
    return _proxy_admin('GET', '/api/admin/reservas')

@app.route('/admin/api/reservas/<int:rid>', methods=['PUT'])
def admin_reserva_put(rid):
    return _proxy_admin('PUT', f'/api/admin/reservas/{rid}', json=request.get_json())

# Temáticas
@app.route('/admin/api/tematicas', methods=['GET'])
def admin_tematicas_get():
    return _proxy_admin('GET', '/api/admin/tematicas')

@app.route('/admin/api/tematicas', methods=['POST'])
def admin_tematicas_post():
    return _proxy_admin('POST', '/api/admin/tematicas', json=request.get_json())

@app.route('/admin/api/tematicas/<int:tid>', methods=['DELETE'])
def admin_tematica_delete(tid):
    return _proxy_admin('DELETE', f'/api/admin/tematicas/{tid}')
@app.route('/admin/api/tematicas/<int:tid>', methods=['PUT'])
def admin_tematicas_put(tid):
    return _proxy_admin('PUT', f'/api/admin/tematicas/{tid}', json=request.get_json())
# Upload de imagen de plato
@app.route('/admin/api/upload-imagen', methods=['POST'])
def admin_upload_imagen():
    if 'imagen' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400
    archivo = request.files['imagen']
    if archivo.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400
    if not allowed_file(archivo.filename, ALLOWED_EXT_IMG):
        return jsonify({'error': 'Formato no permitido. Usa PNG, JPG o WEBP'}), 400
    nombre = secure_filename(archivo.filename)
    ruta = os.path.join(UPLOAD_FOLDER_IMG, nombre)
    archivo.save(ruta)
    # Se guarda 'platos/nombre.jpg' para que las vistas usen url_for('static', filename='img/' + imagen)
    return jsonify({'url': f'platos/{nombre}'})

# Upload de comprobante de transferencia para reserva
@app.route('/api/reservas/comprobante', methods=['POST'])
def subir_comprobante_reserva():
    try:
        reserva_id = request.form.get('reserva_id')
        if not reserva_id:
            return jsonify({'success': False, 'message': 'ID de reserva no proporcionado'}), 400

        if 'archivo' not in request.files:
            return jsonify({'success': False, 'message': 'No se envió ningún archivo'}), 400
        
        archivo = request.files['archivo']
        if archivo.filename == '':
            return jsonify({'success': False, 'message': 'Nombre de archivo vacío'}), 400
        
        if not allowed_file(archivo.filename, ALLOWED_EXT_COMPROBANTE):
            return jsonify({'success': False, 'message': 'Formato no permitido. Usa PNG, JPG o PDF'}), 400
        
        # Obtener cédula del cliente desde la reserva
        conn = conectar()
        if not conn:
            return jsonify({'success': False, 'message': 'Error de conexión a base de datos'}), 500
        
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT c.cc_cliente 
                FROM reservas r
                JOIN clientes c ON r.cliente_id = c.cliente_id
                WHERE r.reserva_id = %s
            """, (reserva_id,))
            resultado = cursor.fetchone()
            
            if not resultado:
                cursor.close()
                conn.close()
                return jsonify({'success': False, 'message': f'Reserva #{reserva_id} no encontrada'}), 404
            
            cedula = resultado['cc_cliente']
            
            # Generar nombre del archivo con cédula
            ext = archivo.filename.rsplit('.', 1)[1].lower()
            nombre = f"comprobante_{cedula}.{ext}"
            ruta = os.path.join(UPLOAD_FOLDER_COMPROBANTES, nombre)
            archivo.save(ruta)
            
            # Verificar si la columna existe, si no, crearla
            cursor.execute("SHOW COLUMNS FROM reservas LIKE 'comprobante_transferencia'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE reservas ADD COLUMN comprobante_transferencia VARCHAR(255) NULL")
                conn.commit()
            
            # Actualizar con la ruta del comprobante, marcar el pago como transferencia
            # y dejar la reserva en espera hasta que admin valide el soporte.
            ruta_relativa = f'comprobantes/{nombre}'
            cursor.execute(
                "UPDATE reservas SET comprobante_transferencia=%s, pago_transferencia=1, estado='en espera' WHERE reserva_id=%s",
                (ruta_relativa, reserva_id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Comprobante recibido correctamente'}), 200
        except Exception as e:
            cursor.close()
            conn.close()
            print(f"Error al guardar en BD: {e}")
            return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500
    except Exception as e:
        print(f"Error en subir_comprobante: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ── Proxy domicilios (cliente → microservicio 5004) ─────────────────────────
@app.route('/api/domicilios', methods=['POST'])
def proxy_crear_domicilio():
    try:
        resp = requests.post('http://localhost:5004/api/domicilios',
                             json=request.get_json(), timeout=30)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 502

# Proxy plato individual (usado por panel.js para editar producto)
@app.route('/api/plato/<int:pid>', methods=['GET'])
def proxy_plato_detalle(pid):
    try:
        resp = requests.get(f'http://localhost:5001/api/plato/{pid}', timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)