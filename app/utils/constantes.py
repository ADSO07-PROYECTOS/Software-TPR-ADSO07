"""
Constantes globales del proyecto Sabores Unidos.
"""
import os

# ─── Carpetas de subida ───────────────────────────────────────────────
CARPETA_IMAGENES = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img', 'platos')
CARPETA_COMPROBANTES = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'comprobantes')

os.makedirs(CARPETA_IMAGENES, exist_ok=True)
os.makedirs(CARPETA_COMPROBANTES, exist_ok=True)

# ─── Extensiones permitidas ──────────────────────────────────────────
EXTENSIONES_IMAGEN = {'png', 'jpg', 'jpeg', 'webp'}
EXTENSIONES_COMPROBANTE = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_TAMANO_COMPROBANTE = 5 * 1024 * 1024  # 5 MB

# ─── Roles ───────────────────────────────────────────────────────────
ROLES_VALIDOS = {'cliente', 'cajero', 'administrador'}

# ─── Días y meses en español ─────────────────────────────────────────
DIAS_ES = ['LUNES', 'MARTES', 'MIÉRCOLES', 'JUEVES', 'VIERNES', 'SÁBADO', 'DOMINGO']
MESES_ES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
            'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

# ─── URLs de microservicios ─────────────────────────────────────────
URL_MICROSERVICIO_MENU = 'http://localhost:5001'
URL_MICROSERVICIO_DOMICILIOS = 'http://localhost:5004'
URL_MICROSERVICIO_RESERVAS = 'http://localhost:5005'
URL_MICROSERVICIO_ADMIN = 'http://localhost:5006'
URL_MICROSERVICIO_MIS_RESERVAS = 'http://localhost:5007'
URL_SERVIDOR_PUBLICO = 'http://147.182.238.195:5000'
