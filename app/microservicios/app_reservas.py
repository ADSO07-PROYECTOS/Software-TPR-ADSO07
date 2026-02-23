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

@app.route('/api/tematicas', methods=['GET'])
def obtener_tematicas():
    conn = conectar()
    if not conn: 
        return jsonify([])
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT tematica_id, nombre_tematica, precio_tematica FROM tematica")
        filas = cursor.fetchall()
        
        tematicas = []
        for f in filas:
            tematicas.append({
                "id": f[0],
                "nombre": f[1],
                "precio": f[2]
            })
        return jsonify(tematicas)
    except Exception as e:
        print(f"Error al obtener temáticas: {e}")
        return jsonify([])
    finally:
        conn.close()

@app.route('/api/reservas', methods=['POST'])
def crear_reserva():
    datos = request.json
    cli = datos.get('cliente')
    res_data = datos.get('reserva')
    
    conn = conectar()
    if not conn: 
        return jsonify({"status": "error", "msg": "Error de conexión a la base de datos"}), 500
    
    cursor = conn.cursor()
    try:
        # --- 1. DEFINICIÓN DE VARIABLES ---
        piso_solicitado = int(res_data['piso'])
        fecha_hora_solicitada = f"{res_data['fec']} {res_data['hor']}:00"
        cedula = int(cli['doc'])

        # --- 2. VALIDACIÓN DE DISPONIBILIDAD (EL CORAZÓN DE TU LÓGICA) ---
        
        # A. Contamos cuántas mesas habilitó el admin para este piso
        cursor.execute("""
            SELECT COUNT(*) FROM mesa 
            WHERE piso = %s AND disponibilidad = 1
        """, (piso_solicitado,))
        max_capacidad_piso = cursor.fetchone()[0]

        # B. Contamos cuántas reservas activas ya existen para ese mismo piso, fecha y hora
        cursor.execute("""
            SELECT COUNT(*) FROM reserva 
            WHERE piso = %s 
            AND fechayhora_reserva = %s 
            AND estado != 'cancelada'
        """, (piso_solicitado, fecha_hora_solicitada))
        reservas_actuales = cursor.fetchone()[0]

        # C. Comparación: ¿Hay espacio?
        if reservas_actuales >= max_capacidad_piso:
            return jsonify({
                "status": "error", 
                "msg": f"Capacidad agotada. El Piso {piso_solicitado} solo permite {max_capacidad_piso} reservas simultáneas y ya están ocupadas."
            }), 400 

        # --- 3. PROCESO DE REGISTRO (SI PASÓ LA VALIDACIÓN) ---

        # Registrar/Actualizar Cliente
        cursor.execute("""
            INSERT INTO clientes (cc_cliente, nombre, email, telefono) 
            VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE nombre=%s, telefono=%s, email=%s
        """, (cedula, cli['nom'], cli['correo'], cli['tel'], cli['nom'], cli['tel'], cli['correo']))

        # Insertar Reserva (mesa_id queda NULL para asignación manual posterior)
        p_trans = 1 if res_data.get('metodo_pago') == 'transferencia' else 0
        query_res = """
            INSERT INTO reserva (
                cc_cliente, cantidad_personas, fechayhora_reserva, mesa_id, 
                piso, tematica_id, estado, estado_pedido, subtotal, pago_transferencia
            ) 
            VALUES (%s, %s, %s, NULL, %s, %s, '1', '1', 0, %s)
        """
        valores_res = (cedula, int(res_data['personas']), fecha_hora_solicitada, 
                       piso_solicitado, int(res_data['tematica']), p_trans)
        
        cursor.execute(query_res, valores_res)
        res_id = cursor.lastrowid

        # Obtener nombre temática para el QR
        cursor.execute("SELECT nombre_tematica FROM tematica WHERE tematica_id = %s", (int(res_data['tematica']),))
        fila_t = cursor.fetchone()
        nombre_t = fila_t[0] if fila_t else "General"

        conn.commit()

        # --- 4. GENERACIÓN DE RESPUESTA (QR) ---
        detalles_qr = (
            f"RESERVA: #{res_id}\n"
            f"CLIENTE: {cli['nom']}\n"
            f"PERSONAS: {res_data['personas']}\n"
            f"PISO: {piso_solicitado}\n"
            f"HORA: {fecha_hora_solicitada}\n"
            f"TEMATICA: {nombre_t}\n"
            f"ESTADO: PENDIENTE ASIGNAR MESA"
        )
        
        qr = qrcode.make(detalles_qr)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        
        enviar_mail_reserva(cli, res_data, buf) # Tu función de correo

        return jsonify({
            "status": "success", 
            "qr": base64.b64encode(buf.getvalue()).decode(), 
            "id": res_id
        })

    except Exception as e:
        if conn: conn.rollback()
        return jsonify({"status": "error", "msg": str(e)}), 500
    finally:
        if conn: conn.close()
            

if __name__ == '__main__':
    app.run(debug=True, port=5005)