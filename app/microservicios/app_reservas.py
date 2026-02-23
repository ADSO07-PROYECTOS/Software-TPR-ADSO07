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

def enviar_mail_reserva(cli, res_data, qr_buf, res_id, nombre_t):
    msg = MIMEMultipart()
    msg["From"] = f"Restaurante Tres Pasos <{MI_CORREO}>"
    msg["To"] = cli['correo']
    msg["Subject"] = f"Confirmación de Reserva #{res_id}"
    
    html = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡RESERVA CONFIRMADA!</h2>
            <p>Hola <b>{cli['nom']}</b>, tu mesa ha sido apartada.</p>
            <p><b>Fecha:</b> {res_data['fec']} | <b>Bloque:</b> {res_data['hor_label']}</p>
            <p><b>Temática:</b> {nombre_t} | <b>Piso:</b> {res_data['piso']}</p>
            <img src="cid:qr_img" style="width: 200px;">
        </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))
    qr_buf.seek(0)
    img = MIMEImage(qr_buf.read())
    img.add_header('Content-ID', '<qr_img>')
    msg.attach(img)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(MI_CORREO, MI_PASSWORD)
            server.sendmail(MI_CORREO, cli['correo'], msg.as_string())
    except Exception as e: print(f"Error Mail: {e}")

@app.route('/api/tematicas', methods=['GET'])
def obtener_tematicas():
    conn = conectar()
    if not conn: return jsonify([])
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica, valor_tematica FROM tematicas")
        return jsonify(cursor.fetchall())
    except: return jsonify([])
    finally: conn.close()

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    datos = request.json
    cli = datos.get('cliente')
    res_data = datos.get('reserva')
    pedido = datos.get('pedido', [])
    
    conn = conectar()
    cursor = conn.cursor()
    try:
        fecha_hora_sql = f"{res_data['fec']} {res_data['hor']}:00"
        cursor.execute("""
            SELECT reserva_id FROM reservas 
            WHERE fecha_hora = %s AND mesa_id = 4 AND estado != 'Cancelada'
        """, (fecha_hora_sql,))
        
        if cursor.fetchone():
            return jsonify({"status": "error", "msg": "Este horario ya está ocupado."}), 400

        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono) 
            VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE nombre=%s
        """, (cli['doc'], cli['nom'], cli['correo'], cli['tel'], cli['nom']))
        cursor.execute("SELECT cliente_id FROM clientes WHERE cc_cliente = %s", (cli['doc'],))
        cliente_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO reservas (cliente_id, mesa_id, tematica_id, fecha_hora, estado) 
            VALUES (%s, 4, %s, %s, 'Confirmada')
        """, (cliente_id, int(res_data['tematica']), fecha_hora_sql))
        res_id = cursor.lastrowid

        for item in pedido:
            cursor.execute("""
                INSERT INTO detalles_reservas (reserva_id, producto_id, cantidad, valor_unitario)
                VALUES (%s, %s, %s, %s)
            """, (res_id, item['id'], item['cantidad'], item['precio']))

        cursor.execute("SELECT nombre_tematica FROM tematicas WHERE tematica_id = %s", (int(res_data['tematica']),))
        fila_t = cursor.fetchone()
        nombre_t = fila_t[0] if fila_t else "General"
        
        conn.commit()

        detalles_qr = (
            f"--- TRES PASOS RESERVA ---\n"
            f"CLIENTE: {cli['nom'].upper()}\n"
            f"BLOQUE: {res_data['hor_label']}\n"
            f"FECHA: {res_data['fec']}\n"
            f"PERSONAS: {res_data['personas']}\n"
            f"PISO: {res_data['piso']}\n"
            f"TEMATICA: {nombre_t}\n"
            f"--------------------------"
        )
        qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

        qr.add_data(detalles_qr.encode('utf-8')) 
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        
        enviar_mail_reserva(cli, res_data, buf, res_id, nombre_t)
        return jsonify({"status": "success", "id": res_id, "qr": base64.b64encode(buf.getvalue()).decode()})

    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "msg": str(e)}), 500
    finally: conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5004)