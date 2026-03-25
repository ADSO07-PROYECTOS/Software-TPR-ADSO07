import sys, os, qrcode, io, base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', '.env'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from conexion import conectar

app = Flask(__name__)
CORS(app)

URL_SERVIDOR_PUBLICO = os.environ.get("URL_SERVIDOR_PUBLICO", "http://192.168.215.37:5000")

DIAS_ES = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
MESES_ES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
            'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']


# ─── Consultar reservas por cédula ──────────────────────────────────

@app.route('/api/mis_reservas', methods=['GET'])
def consultar_reservas():
    cedula = request.args.get('cedula', '').strip()
    if not cedula:
        return jsonify({"error": "Parámetro 'cedula' requerido"}), 400

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
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

        for reserva in reservas:
            fecha_hora = reserva['fecha_hora']
            if fecha_hora:
                reserva['fecha_formato'] = (
                    f"{DIAS_ES[fecha_hora.weekday()]}, {fecha_hora.day} "
                    f"{MESES_ES[fecha_hora.month - 1]}, "
                    f"{fecha_hora.strftime('%I:%M %p')}"
                )
                reserva['fecha_hora'] = fecha_hora.strftime('%Y-%m-%d %H:%M:%S')
            else:
                reserva['fecha_formato'] = ''
                reserva['fecha_hora'] = ''

            # Pedido asociado
            cursor.execute("""
                SELECT p.nombre_producto, dr.cantidad, dr.notas
                FROM detalles_reservas dr
                JOIN productos p ON dr.producto_id = p.producto_id
                WHERE dr.reserva_id = %s
            """, (reserva['reserva_id'],))
            reserva['pedido'] = cursor.fetchall()

            # QR
            url_qr = f"{URL_SERVIDOR_PUBLICO}/resumen/reserva/{reserva['reserva_id']}"
            imagen_qr = qrcode.make(url_qr)
            buffer = io.BytesIO()
            imagen_qr.save(buffer, format="PNG")
            reserva['qr_b64'] = base64.b64encode(buffer.getvalue()).decode()

        sin_resultados = len(reservas) == 0
        return jsonify({"reservas": reservas, "sin_resultados": sin_resultados})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ─── Obtener reserva para modificar ─────────────────────────────────

@app.route('/api/mis_reservas/<int:id_reserva>', methods=['GET'])
def obtener_reserva(id_reserva):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT r.reserva_id, r.fecha_hora, r.cantidad_personas, r.tematica_id, r.estado,
                   c.nombre, c.email, c.telefono, c.cc_cliente
            FROM reservas r
            JOIN clientes c ON r.cliente_id = c.cliente_id
            WHERE r.reserva_id = %s
        """, (id_reserva,))
        reserva = cursor.fetchone()

        if not reserva:
            return jsonify({"error": "Reserva no encontrada"}), 404

        if reserva['fecha_hora']:
            reserva['fecha_hora'] = reserva['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(reserva)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ─── Actualizar reserva ─────────────────────────────────────────────

@app.route('/api/mis_reservas/<int:id_reserva>', methods=['PUT'])
def actualizar_reserva(id_reserva):
    datos = request.json
    if not datos:
        return jsonify({"error": "Datos requeridos"}), 400

    fecha_hora = datos.get('fecha_hora')
    personas = datos.get('personas')
    tematica = datos.get('tematica')
    nombre = datos.get('nombre')
    email = datos.get('email')
    telefono = datos.get('telefono')

    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE reservas
            SET fecha_hora = %s, cantidad_personas = %s, tematica_id = %s
            WHERE reserva_id = %s
        """, (fecha_hora, personas, tematica, id_reserva))

        cursor.execute("""
            UPDATE clientes c
            JOIN reservas r ON r.cliente_id = c.cliente_id
            SET c.nombre = %s, c.email = %s, c.telefono = %s
            WHERE r.reserva_id = %s
        """, (nombre, email, telefono, id_reserva))

        conn.commit()
        return jsonify({"status": "success", "message": "Reserva actualizada correctamente"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ─── Eliminar reserva ───────────────────────────────────────────────

@app.route('/api/mis_reservas/<int:id_reserva>', methods=['DELETE'])
def eliminar_reserva(id_reserva):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM detalles_reservas WHERE reserva_id = %s", (id_reserva,))
        cursor.execute("DELETE FROM reservas WHERE reserva_id = %s", (id_reserva,))
        conn.commit()
        return jsonify({"status": "success", "message": "Reserva eliminada correctamente"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# ─── Tematicas (para el formulario de modificar) ────────────────────

@app.route('/api/tematicas', methods=['GET'])
def listar_tematicas():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
        return jsonify(cursor.fetchall())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5007)
