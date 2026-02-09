import smtplib, ssl, qrcode, io, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MI_CORREO = "e5toesparapruebas12@gmail.com" 
MI_PASSWORD = "nmus gbvy uxtl ycte"

def enviar_mail(datos_cliente, datos_reserva, qr_buf):
    msg = MIMEMultipart()
    msg["From"] = MI_CORREO
    msg["To"] = datos_cliente['correo']
    msg["Subject"] = f"Reserva Confirmada - {datos_cliente['nom']}"

    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; text-align: center;">
            <h2 style="color: #e67e22;">¡Reserva Confirmada en Tres Pasos!</h2>
            <p>Hola <b>{datos_cliente['nom']}</b>, hemos agendado tu mesa con éxito.
            </p>
            <div style="background: #f4f4f4; padding: 15px; border-radius: 10px; display: inline-block; margin: 10px 0;">
                <p><b>Fecha:</b> {datos_reserva['fec']}</p>
                <p><b>Hora:</b> {datos_reserva['hor']}</p>
            </div>
            <p>Muestra este código QR al llegar al restaurante:</p>
            <img src="cid:qr_img" style="width: 200px;">
        </body>
    </html>
    """
    msg.attach(MIMEText(cuerpo_html, "html"))

    qr_buf.seek(0)
    img_adjunta = MIMEImage(qr_buf.read())
    img_adjunta.add_header('Content-ID', '<qr_img>')
    msg.attach(img_adjunta)

    try:
        contexto = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=contexto) as server:
            server.login(MI_CORREO, MI_PASSWORD)
            server.sendmail(MI_CORREO, datos_cliente['correo'], msg.as_string())
        return True
    except Exception as e:
        print(f"Error enviando mail: {e}")
        return False

@app.route('/api/reservas', methods=['POST'])
def gestionar():
    datos = request.json
    id_res = "789"  #numero que sera reemplazado cuando este los id de la bd

    texto_qr = f"ID: {id_res}\nCLIENTE: {datos['cliente']['nom']}\nFECHA: {datos['reserva']['fec']}\nHORA: {datos['reserva']['hor']}"
    img = qrcode.make(texto_qr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    
    b64 = base64.b64encode(buf.getvalue()).decode()
    enviar_mail(datos['cliente'], datos['reserva'], buf)

    return jsonify({"status": "success", "qr": b64})

if __name__ == '__main__':
    app.run(debug=True, port=5000)