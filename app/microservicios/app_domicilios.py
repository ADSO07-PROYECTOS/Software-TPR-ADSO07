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
    direccion = datos.get('direccion')
    
    conn = conectar()
    if not conn: 
        return jsonify({"status": "error", "msg": "Error de conexión a la base de datos"}), 500
    
    cursor = conn.cursor()
    try:
        cedula = int(cli['doc'])
        
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono) 
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE nombre=%s, telefono=%s, email=%s
        """, (cedula, cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['tel'], cli['correo']))
        
        cursor.execute("SELECT cliente_id FROM clientes WHERE cc_cliente = %s", (cedula,))
        cliente_id = cursor.fetchone()[0]

        pago = 1 if datos.get('pago_transferencia') == '1' else 0
        
        query_dom = """
            INSERT INTO domicilios (cliente_id, direccion, pago_transferencia, estado_pedido) 
            VALUES (%s, %s, %s, 'Pendiente')
        """
        cursor.execute(query_dom, (cliente_id, direccion, pago))
        
        dom_id = cursor.lastrowid
        conn.commit()

        detalles_qr = (
            f"TRES PASOS - DOMICILIO\n"
            f"PEDIDO: #{dom_id}\n"
            f"CLIENTE: {cli['nom']}\n"
            f"DIRECCIÓN: {direccion}\n"
            f"PAGO: {'Transferencia' if pago == 1 else 'Efectivo'}\n"
            f"ESTADO: EN PREPARACIÓN"
        )
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        
        enviar_mail_dom(cli, direccion, buf, dom_id)

        return jsonify({
            "status": "success", 
            "id": dom_id, 
            "qr": base64.b64encode(buf.getvalue()).decode()
        })

    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"status": "error", "msg": f"Error en el servidor: {str(e)}"}), 500
    finally: 
        if conn: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)