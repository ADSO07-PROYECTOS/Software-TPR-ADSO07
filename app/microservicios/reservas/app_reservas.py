import sys, os, qrcode, io, base64, threading, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import locale
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', '.env'))

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from conexion import conectar

app = Flask(__name__)
CORS(app)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Sabores Unidos")

URL_SERVIDOR = os.environ.get("URL_SERVIDOR_PUBLICO", "http://54.156.114.70:62001")
LOGO_URL = f"{URL_SERVIDOR}/static/img/sabores-unidos.png"

def formato_hora_12h(hora_str):
    """Convierte '14' o '14:00' a '2:00 PM'."""
    h = int(str(hora_str).split(':')[0])
    sufijo = 'AM' if h < 12 else 'PM'
    h12 = h % 12 or 12
    return f"{h12}:00 {sufijo}"

def enviar_mail_reserva(datos_cliente, datos_reserva, qr_buf, res_id):
    qr_buf.seek(0)
    qr_b64 = base64.b64encode(qr_buf.read()).decode()

    hora_12 = formato_hora_12h(datos_reserva['hor'])
    cedula = datos_cliente['doc']
    url_mis_reservas = f"{URL_SERVIDOR}/mis_reservas?cedula={cedula}"

    cuerpo = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; margin: 0; padding: 0;">
            <div style="max-width: 520px; margin: 20px auto; background: #2b2b2b; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                <div style="background-color: #99181F; padding: 20px; text-align: center;">
                    <img src="{LOGO_URL}" alt="Sabores Unidos" style="height: 70px;">
                </div>
                <div style="padding: 25px 30px; text-align: center; color: #e0e0e0;">
                    <h2 style="color: #ff4d4d; margin-top: 0;">¡Reserva Confirmada!</h2>
                    <p style="font-size: 16px;">Hola <b style="color: #fff;">{datos_cliente['nom']}</b>, tu mesa ha sido reservada con éxito.</p>
                    <div style="background: #3a2020; border-radius: 8px; padding: 15px; margin: 15px 0; border: 1px solid #99181F;">
                        <p style="margin: 5px 0; color: #e0e0e0;"><b>Fecha:</b> {datos_reserva['fec']}</p>
                        <p style="margin: 5px 0; color: #e0e0e0;"><b>Hora:</b> {hora_12}</p>
                        <p style="margin: 5px 0; color: #e0e0e0;"><b>Reserva #:</b> {res_id}</p>
                    </div>
                    <p style="font-size: 14px; color: #aaa;">El código QR de tu reserva va adjunto en este correo. Preséntalo al llegar al restaurante.</p>
                    <div style="margin-top: 25px;">
                        <p style="font-size: 14px; color: #aaa;">¿Necesitas modificar o cancelar tu reserva?</p>
                        <a href="{url_mis_reservas}" style="display: inline-block; background-color: #99181F; color: #fff; text-decoration: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; margin-top: 5px;">Gestionar mi reserva</a>
                    </div>
                </div>
                <div style="background: #1a1a1a; text-align: center; padding: 12px; font-size: 12px; color: #666;">
                    Sabores Unidos &copy; 2026 — Todos los derechos reservados
                </div>
            </div>
        </body>
    </html>
    """
    try:
        resp = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": BREVO_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "sender": {"name": BREVO_SENDER_NAME, "email": BREVO_SENDER_EMAIL},
                "to": [{"email": datos_cliente['correo']}],
                "subject": f"Confirmación de Reserva #{res_id} - Sabores Unidos",
                "htmlContent": cuerpo,
                "attachment": [{
                    "content": qr_b64,
                    "name": "qr_reserva.png",
                    "type": "image/png"
                }],
                "headers": {
                    "X-Mailin-custom": f"reserva_{res_id}"
                }
            },
            timeout=30
        )
        if resp.status_code not in (200, 201):
            print(f"Error Brevo reserva: {resp.status_code} - {resp.text}")
        else:
            print(f"Correo de reserva enviado correctamente: {resp.json()}")
    except Exception as e:
        import traceback
        print(f"Error enviando mail de reserva: {e}")
        traceback.print_exc()

@app.route('/api/tematicas', methods=['GET'])
def obtener_tematicas():
    conn = conectar()
    cursor = conn.cursor(dictionary=True) 
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
        filas = cursor.fetchall()
        return jsonify(filas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    datos = request.json
    cli = datos.get('cliente')
    res_data = datos.get('reserva')
    pedido = datos.get('pedido', [])

    if not cli or not res_data:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        hora_str = res_data['hor'].split(':')[0] if ':' in res_data['hor'] else res_data['hor']
        hora_limpia = f"{int(hora_str):02d}:00:00"
        fecha_hora_sql = f"{res_data['fec']} {hora_limpia}"

        
        query_disponibilidad = """
            SELECT mesa_id FROM mesas 
            WHERE piso = %s 
            AND mesa_id NOT IN (
                SELECT mesa_id FROM reservas 
                WHERE fecha_hora = %s
            ) 
            LIMIT 1
        """
        cursor.execute(query_disponibilidad, (res_data['piso'], fecha_hora_sql))
        mesa_disponible = cursor.fetchone()

        if not mesa_disponible:
            return jsonify({
                "status": "error", 
                "message": "Lo sentimos, no hay mesas disponibles en el piso seleccionado para esta hora."
            }), 409

        id_mesa_asignada = mesa_disponible['mesa_id']

        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono)
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE nombre=%s, email=%s, telefono=%s
        """, (cli['doc'], cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['correo'], cli['tel']))

        cursor.execute("SELECT cliente_id FROM clientes WHERE cc_cliente = %s", (cli['doc'],))
        cliente_id = cursor.fetchone()['cliente_id']

        metodo_pago = str(res_data.get('metodo_pago', res_data.get('pago', '0')))
        p_trans = 1 if metodo_pago == '1' else 0
        estado = 'en espera' if p_trans else 'confirmada'
        query_res = """
            INSERT INTO reservas (cliente_id, mesa_id, cantidad_personas, fecha_hora, tematica_id, estado, pago_transferencia)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query_res, (
            cliente_id, 
            id_mesa_asignada,
            res_data['personas'], 
            fecha_hora_sql,
            res_data['tematica'], 
            estado,
            p_trans
        ))
        res_id = cursor.lastrowid

        for p in pedido:
            prod_id = p.get('id')
            if not prod_id:
                continue
            partes = []
            if p.get('tamano'):
                partes.append(p['tamano'].upper())
            adicionales = p.get('adicionales', [])
            if adicionales:
                partes.append('Adicionales: ' + ', '.join(adicionales))
            sabores = p.get('sabores', [])
            if sabores:
                partes.append('Sabores: ' + ', '.join(sabores))
            notas = ' | '.join(partes) if partes else None
            cursor.execute("""
                INSERT INTO detalles_reservas (reserva_id, producto_id, cantidad, valor_unitario, notas)
                VALUES (%s, %s, %s, %s, %s)
            """, (res_id, prod_id, p.get('cantidad', 1), p.get('precio', 0), notas))

        conn.commit()

        detalles_qr = f"http://54.156.114.70:62001/resumen/reserva/{res_id}"
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        threading.Thread(
            target=enviar_mail_reserva,
            args=(cli, res_data, buf, res_id),
            daemon=True
        ).start()

        return jsonify({
            "status": "success", 
            "message": f"Reserva creada con éxito en la mesa {id_mesa_asignada}",
            "id": res_id,
            "qr": qr_b64
        })

    except Exception as e:
        print(f"Error en validación/reserva: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)