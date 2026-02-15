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

def enviar_mail_qr(datos_cliente, texto_qr, qr_buf):
    msg = MIMEMultipart()
    msg["From"] = MI_CORREO
    msg["To"] = datos_cliente['correo']
    msg["Subject"] = f"Confirmación de Pedido - Tres Pasos"

    cuerpo = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡Tu pedido está en camino!</h2>
            <p>Hola <b>{datos_cliente['nom']}</b>, hemos recibido tu solicitud de domicilio.</p>
            <p><b>Dirección:</b> {datos_cliente.get('direccion', 'Ver QR')}</p>
            <img src="cid:qr_img" style="width: 200px; border: 2px solid #99181F;">
            <p>Muestra este código al repartidor.</p>
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
            server.sendmail(MI_CORREO, datos_cliente['correo'], msg.as_string())
        return True
    except: return False

@app.route('/api/domicilios', methods=['POST'])
def crear_domicilio():
    datos = request.json
    cli = datos['cliente']
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono) 
            VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s
        """, (cli['doc'], cli['nom'], cli['correo'], cli['tel'], cli['nom']))
        conn.commit()

        # QR
        texto_qr = f"DOMICILIO\nCliente: {cli['nom']}\nDireccion: {datos.get('direccion')}"
        qr = qrcode.make(texto_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        
        # Correo
        cli['direccion'] = datos.get('direccion')
        enviar_mail_qr(cli, texto_qr, buf)

        return jsonify({"status": "success", "qr": base64.b64encode(buf.getvalue()).decode()})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500
    finally: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5001)