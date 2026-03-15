import sys, os, qrcode, io, base64, threading, requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carga variables de entorno desde .env en la raiz del proyecto
load_dotenv(os.path.join(os.path.dirname(__file__), '../../..', '.env'))

app = Flask(__name__)
CORS(app)

BREVO_API_KEY = os.environ.get("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "Tres Pasos")

def enviar_mail_dom(cli, direccion, qr_buf, dom_id):
    qr_buf.seek(0)
    qr_b64 = base64.b64encode(qr_buf.read()).decode()

    cuerpo = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡Pedido Recibido!</h2>
            <p>Hola <b>{cli['nom']}</b>, estamos preparando tu pedido.</p>
            <p><b>ID del Pedido:</b> #{dom_id}</p>
            <p><b>Dirección de entrega:</b> {direccion}</p>
            <img src="data:image/png;base64,{qr_b64}" style="width: 200px; border: 2px solid #99181F;">
            <p>Escanea este código para ver los detalles de tu entrega.</p>
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
                "subject": f"Confirmación de Pedido - Tres Pasos #{dom_id}",
                "htmlContent": cuerpo
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
                continue  # Ignorar ítems sin producto_id válido
            cursor.execute("""
                INSERT INTO detalles_domicilios (domicilio_id, producto_id, cantidad, valor_unitario)
                VALUES (%s, %s, %s, %s)
            """, (dom_id, prod_id, p.get('cantidad', 1), p.get('precio', 0)))

        conn.commit()
        detalles_qr = f"http://147.182.238.195:5000/resumen/domicilio/{dom_id}"
        
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