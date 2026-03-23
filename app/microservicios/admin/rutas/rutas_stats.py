from flask import Blueprint, jsonify
from conexion import conectar

mod_stats = Blueprint('stats', __name__)


@mod_stats.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    stats = {
        'domicilios_hoy': 0, 'domicilios_pendientes': 0,
        'mesas_disponibles': 0, 'mesas_ocupadas': 0, 'mesas_reservadas': 0,
    }
    mesas_por_piso = []
    pedidos_recientes = []
    try:
        conn = conectar()
        if conn:
            cursor = conn.cursor(dictionary=True)

            cursor.execute(
                "SELECT COUNT(*) AS c FROM domicilios WHERE DATE(fecha_hora) = CURDATE()"
            )
            row = cursor.fetchone()
            stats['domicilios_hoy'] = row['c'] if row else 0

            cursor.execute(
                "SELECT COUNT(*) AS c FROM domicilios WHERE estado_pedido = 'Pendiente'"
            )
            row = cursor.fetchone()
            stats['domicilios_pendientes'] = row['c'] if row else 0

            cursor.execute("""
                SELECT m.piso,
                    COUNT(*) AS total,
                    SUM(CASE WHEN r.reserva_id IS NOT NULL AND r.estado IN ('confirmada', 'en espera') THEN 1 ELSE 0 END) AS reservadas,
                    SUM(CASE WHEN r.reserva_id IS NOT NULL AND r.estado = 'ocupada'    THEN 1 ELSE 0 END) AS ocupadas
                FROM mesas m
                LEFT JOIN reservas r ON m.mesa_id = r.mesa_id AND DATE(r.fecha_hora) = CURDATE()
                GROUP BY m.piso
                ORDER BY m.piso
            """)
            for fila in cursor.fetchall():
                reservadas  = int(fila['reservadas'] or 0)
                ocupadas    = int(fila['ocupadas']   or 0)
                total       = int(fila['total'])
                disponibles = max(total - reservadas - ocupadas, 0)
                mesas_por_piso.append({
                    'piso': fila['piso'],
                    'total': total,
                    'reservadas': reservadas,
                    'ocupadas': ocupadas,
                    'disponibles': disponibles,
                })
                stats['mesas_disponibles'] += disponibles
                stats['mesas_ocupadas']    += ocupadas
                stats['mesas_reservadas']  += reservadas

            cursor.execute("""
                SELECT d.domicilio_id, d.estado_pedido, d.fecha_hora,
                       c.nombre, d.direccion
                FROM domicilios d
                LEFT JOIN clientes c ON d.cliente_id = c.cliente_id
                ORDER BY d.fecha_hora DESC LIMIT 5
            """)
            for row in cursor.fetchall():
                row['fecha_hora'] = str(row['fecha_hora']) if row.get('fecha_hora') else None
                pedidos_recientes.append(row)

            cursor.close()
            conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        'stats': stats,
        'mesas_por_piso': mesas_por_piso,
        'pedidos_recientes': pedidos_recientes,
    })
