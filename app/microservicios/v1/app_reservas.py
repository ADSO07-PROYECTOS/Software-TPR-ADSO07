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

def enviar_mail_reserva(datos_cliente, datos_reserva, qr_buf):
    msg = MIMEMultipart()
    msg["From"] = MI_CORREO
    msg["To"] = datos_cliente['correo']
    msg["Subject"] = "Confirmación de Reserva - Tres Pasos"
    
    cuerpo = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡Reserva Confirmada!</h2>
            <p>Hola <b>{datos_cliente['nom']}</b>, tu mesa ha sido reservada con éxito.</p>
            <p><b>Fecha:</b> {datos_reserva['fec']} | <b>Hora:</b> {datos_reserva['hor']}</p>
            <img src="cid:qr_img" style="width: 200px; border: 2px solid #99181F;">
            <p>Por favor, presenta este QR al llegar al restaurante.</p>
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
    except Exception as e: print(f"Error mail: {e}")

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    datos = request.json
    cli = datos.get('cliente')
    res = datos.get('reserva')
    
    conn = conectar()
    if not conn: return jsonify({"status": "error", "msg": "Sin conexión a DB"}), 500
    
    cursor = conn.cursor()
    try:
        cedula = int(cli['doc'])
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono) 
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE nombre=%s, telefono=%s, email=%s
        """, (cedula, cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['tel'], cli['correo']))
        
        fec_hora = f"{res['fec']} {res['hor']}:00"
        
        p_trans = 1 if res.get('metodo_pago') == 'transferencia' else 0

        query_res = """
            INSERT INTO reserva (
                cc_cliente, fechayhora_reserva, mesa_id, descripcion_mesa, 
                piso, tematica_id, estado, estado_pedido, subtotal, pago_transferencia
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        valores_res = (
            cedula, 
            fec_hora, 
            1,                 
            res.get('desc', ''), 
            int(res['piso']), 
            int(res['tematica']), 
            '1',               
            '1',                
            0,                  
            p_trans
        )
        
        cursor.execute(query_res, valores_res)
        res_id = cursor.lastrowid
        conn.commit()
        
        #QR
        detalles_qr = (
            f"--- TRES PASOS RESTAURANTE ---\n"
            f"RESERVA: #{res_id}\n"
            f"CLIENTE: {cli['nom']}\n"
            f"DOCUMENTO: {cli['doc']}\n"
            f"FECHA: {res['fec']}\n"
            f"HORA: {res['hor']}\n"
            f"PISO: {res['piso']}\n"
            f"TEMATICA: {res['tematica']}\n"
            f"METODO PAGO: {res.get('metodo_pago', 'Efectivo').upper()}\n"
            f"MESA: {res.get('desc', 'Ninguna')}\n"
            f"------------------------------"
        )

        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        
        enviar_mail_reserva(cli, res, buf)
        
        enviar_mail_reserva(cli, res, buf)

        return jsonify({
            "status": "success", 
            "qr": base64.b64encode(buf.getvalue()).decode(), 
            "id": res_id
        })

    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)