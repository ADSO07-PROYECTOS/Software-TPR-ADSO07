import sys, os, qrcode, io, base64, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from conexion import conectar

app = Flask(__name__)
CORS(app)

MI_CORREO = "e5toesparapruebas12@gmail.com" 
MI_PASSWORD = "nmus gbvy uxtl ycte"

def enviar_mail_dom(cli, direccion, qr_buf, dom_id):
    msg = MIMEMultipart()
    msg["From"] = f"Tres Pasos <{MI_CORREO}>"
    msg["To"] = cli['correo']
    msg["Subject"] = f"Confirmación de Pedido - Tres Pasos #{dom_id}"
    
    cuerpo = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡Pedido Recibido!</h2>
            <p>Hola <b>{cli['nom']}</b>, estamos preparando tu pedido.</p>
            <p><b>ID del Pedido:</b> #{dom_id}</p>
            <p><b>Dirección de entrega:</b> {direccion}</p>
            <img src="cid:qr_img" style="width: 200px; border: 2px solid #99181F;">
            <p>Escanea este código para ver los detalles de tu entrega.</p>
        </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo, "html"))
    
    qr_buf.seek(0)
    img = MIMEImage(qr_buf.read())
    img.add_header('Content-ID', '<qr_img>')
    msg.attach(img)
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MI_CORREO, MI_PASSWORD)
            server.sendmail(MI_CORREO, cli['correo'], msg.as_string())
    except Exception as e: 
        print(f"Error enviando mail de domicilio: {e}")

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
            INSERT INTO clientes (cc_cliente, nombre, email, telefono)
            VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s, email=%s, telefono=%s
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
            cursor.execute("""
                INSERT INTO detalles_domicilios (domicilio_id, producto_id, cantidad, valor_unitario)
                VALUES (%s, %s, %s, %s)
            """, (dom_id, p['id'], p['cantidad'], p['precio']))

        conn.commit()
        detalles_qr = (
            f"DOMICILIO: #{dom_id}\n"
            f"CLIENTE: {cli['nom']}\n"
            f"DIRECCIÓN: {dom['direccion']}\n"
            f"METODO DE PAGO: {dom['metodo_pago']}"
            )
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        enviar_mail_dom(cli, dom['direccion'], buf, dom_id)

        return jsonify({
                    "status": "success", 
                    "message": f"Domicilio creado con éxito con ID #{dom_id}",
                    "qr": qr_b64
                })
        
    
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5004)