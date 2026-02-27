import sys, os, qrcode, io, base64, smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Flask, request, jsonify
from flask_cors import CORS
import locale

# Configuración de rutas para importar conexión
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from conexion import conectar

app = Flask(__name__)
CORS(app)

MI_CORREO = "e5toesparapruebas12@gmail.com" 
MI_PASSWORD = "nmus gbvy uxtl ycte"

def enviar_mail_reserva(datos_cliente, datos_reserva, qr_buf):
    msg = MIMEMultipart()
    msg["From"] = f"Restaurante Tres Pasos <{MI_CORREO}>"
    msg["To"] = datos_cliente['correo']
    msg["Subject"] = "Confirmación de Reserva - Tres Pasos"
    
    cuerpo = f"""
    <html>
        <body style="font-family: Arial; text-align: center;">
            <h2 style="color: #99181F;">¡Reserva Confirmada!</h2>
            <p>Hola <b>{datos_cliente['nom']}</b>, tu mesa ha sido reservada con éxito.</p>
            <p><b>Fecha:</b> {datos_reserva['fec']} | <b>Hora:</b> {datos_reserva['hor']}:00</p>
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
    except Exception as e: 
        print(f"Error enviando mail: {e}")

@app.route('/api/tematicas', methods=['GET'])
def obtener_tematicas():
    conn = conectar()
    cursor = conn.cursor(dictionary=True) # Importante para que el JS reciba nombres y no solo valores
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica FROM tematicas")
        filas = cursor.fetchall()
        return jsonify(filas) # Esto devuelve: [{"tematica_id": 1, "nombre_tematica": "Boda"}, ...]
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
    
    if not cli or not res_data:
        return jsonify({"status": "error", "message": "Datos incompletos"}), 400

    conn = conectar()
    cursor = conn.cursor(dictionary=True) # Usamos diccionario para manejar mejor las mesas
    try:
        # 1. FORMATEAR FECHA Y HORA (Igual que antes)
        hora_limpia = f"{int(res_data['hor']):02d}:00:00"
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
            }), 409 # Código 409: Conflicto

        id_mesa_asignada = mesa_disponible['mesa_id']

        # 3. SINCRONIZAR CLIENTE
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono)
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE nombre=%s, email=%s, telefono=%s
        """, (cli['doc'], cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['correo'], cli['tel']))

        cursor.execute("SELECT cliente_id FROM clientes WHERE cc_cliente = %s", (cli['doc'],))
        cliente_id = cursor.fetchone()['cliente_id']

        # 4. INSERTAR RESERVA CON MESA ASIGNADA
        p_trans = 1 if res_data.get('pago') == '1' else 0
        estado = 'confirmada'
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

        conn.commit()

        detalles_qr = (
            f"RESERVA: #{res_id}\n"
            f"MESA ASIGNADA: {id_mesa_asignada}\n"
            f"CLIENTE: {cli['nom']}\n"
            f"FECHA/HORA: {fecha_hora_sql}"
        )
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        enviar_mail_reserva(cli, res_data, buf)

        return jsonify({
            "status": "success", 
            "message": f"Reserva creada con éxito en la mesa {id_mesa_asignada}",
            "qr": qr_b64
        })

    except Exception as e:
        print(f"Error en validación/reserva: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5005)