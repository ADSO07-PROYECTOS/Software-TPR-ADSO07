import sys, os, qrcode, io, base64, threading, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from conexion import conectar

load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', '.env'))

app = Flask(__name__)
CORS(app)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Sabores Unidos")

URL_SERVIDOR = os.environ.get("URL_SERVIDOR_PUBLICO", "http://54.156.114.70:62001")
LOGO_URL = f"{URL_SERVIDOR}/static/img/sabores-unidos.png"

def enviar_mail_dom(cli, direccion, qr_buf, dom_id):
    qr_buf.seek(0)
    qr_b64 = base64.b64encode(qr_buf.read()).decode()

    cuerpo = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #1a1a1a; margin: 0; padding: 0;">
            <div style="max-width: 520px; margin: 20px auto; background: #2b2b2b; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                <div style="background-color: #99181F; padding: 20px; text-align: center;">
                    <img src="{LOGO_URL}" alt="Sabores Unidos" style="height: 70px;">
                </div>
                <div style="padding: 25px 30px; text-align: center; color: #e0e0e0;">
                    <h2 style="color: #ff4d4d; margin-top: 0;">¡Domicilio Recibido!</h2>
                    <p style="font-size: 16px;">Hola <b style="color: #fff;">{cli['nom']}</b>, estamos preparando tu domicilio.</p>
                    <div style="background: #3a2020; border-radius: 8px; padding: 15px; margin: 15px 0; border: 1px solid #99181F;">
                        <p style="margin: 5px 0; color: #e0e0e0;"><b>📦 Domicilio #:</b> {dom_id}</p>
                        <p style="margin: 5px 0; color: #e0e0e0;"><b>📍 Dirección:</b> {direccion}</p>
                    </div>
                    <p style="font-size: 14px; color: #aaa;">El código QR de tu domicilio va adjunto en este correo. Escanéalo para ver los detalles de tu entrega.</p>
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
                "to": [{"email": cli['correo']}],
                "subject": f"Confirmación de Domicilio #{dom_id} - Sabores Unidos",
                "htmlContent": cuerpo,
                "attachment": [{
                    "content": qr_b64,
                    "name": "qr_domicilio.png",
                    "type": "image/png"
                }],
                "headers": {
                    "X-Mailin-custom": f"domicilio_{dom_id}"
                }
            },
            timeout=30
        )
        if resp.status_code not in (200, 201):
            print(f"Error Brevo domicilio: {resp.status_code} - {resp.text}")
        else:
            print(f"Correo de domicilio enviado correctamente: {resp.json()}")
    except Exception as e:
        import traceback
        print(f"Error enviando mail de domicilio: {e}")
        traceback.print_exc()

@app.route('/api/domicilios', methods=['POST'])
def crear_domicilio():
    datos = request.json
    cli = datos.get('cliente')
    dom = datos.get('domicilio')
    productos = datos.get('productos')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono, rol)
            VALUES (%s, %s, %s, %s, 'cliente')
            ON DUPLICATE KEY UPDATE nombre=%s, email=%s, telefono=%s
        """, (cli['doc'], cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['correo'], cli['tel']))
        
        cursor.execute("SELECT cliente_id FROM clientes WHERE cc_cliente = %s", (cli['doc'],))
        cliente_id = cursor.fetchone()['cliente_id']

        total_pedido = sum(item['precio'] * item['cantidad'] for item in productos)
        query_dom = """
            INSERT INTO domicilios (cliente_id, direccion, pago_transferencia, estado_pedido)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_dom, (cliente_id, dom['direccion'], dom['metodo_pago'] == 'transferencia', 'Pendiente'))
        dom_id = cursor.lastrowid

        for p in productos:
            prod_id = p.get('id')
            if not prod_id:
                continue
            cursor.execute("""
                INSERT INTO detalles_domicilios (domicilio_id, producto_id, cantidad, valor_unitario)
                VALUES (%s, %s, %s, %s)
            """, (dom_id, prod_id, p.get('cantidad', 1), p.get('precio', 0)))

        conn.commit()
        detalles_qr = f"http://54.156.114.70:62001/resumen/domicilio/{dom_id}"
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        threading.Thread(
            target=enviar_mail_dom,
            args=(cli, dom['direccion'], buf, dom_id),
            daemon=True
        ).start()

        return jsonify({
                    "status": "success",
                    "message": f"Domicilio creado con éxito con ID #{dom_id}",
                    "id": dom_id,
                    "qr": qr_b64
                })
        
    
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)