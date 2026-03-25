#!/bin/bash
# ─── Lanzar toda la aplicación Sabores Unidos ─────────────────────
cd /home/dev_py/Software-TPR-ADSO07/app
source venv/bin/activate

# Matar procesos anteriores
pkill -f 'python.*app.py' 2>/dev/null
pkill -f 'python.*menu.py' 2>/dev/null
pkill -f 'python.*app_domicilios' 2>/dev/null
pkill -f 'python.*app_reservas' 2>/dev/null
pkill -f 'python.*app_admin' 2>/dev/null
pkill -f 'python.*app_mis_reservas' 2>/dev/null
sleep 1

mkdir -p /tmp/sabores_logs

# Lanzar microservicios
echo "[+] Lanzando Menu (puerto 5001)..."
nohup python microservicios/menu/menu.py > /tmp/sabores_logs/menu.log 2>&1 &

echo "[+] Lanzando Domicilios (puerto 5004)..."
nohup python microservicios/domicilios/app_domicilios.py > /tmp/sabores_logs/domicilios.log 2>&1 &

echo "[+] Lanzando Reservas (puerto 5005)..."
nohup python microservicios/reservas/app_reservas.py > /tmp/sabores_logs/reservas.log 2>&1 &

echo "[+] Lanzando Admin (puerto 5006)..."
nohup python microservicios/admin/app_admin.py > /tmp/sabores_logs/admin.log 2>&1 &

echo "[+] Lanzando Mis Reservas (puerto 5007)..."
nohup python microservicios/mis_reservas/app_mis_reservas.py > /tmp/sabores_logs/mis_reservas.log 2>&1 &

echo "[+] Lanzando App Principal (puerto 5000)..."
nohup python app.py > /tmp/sabores_logs/app.log 2>&1 &

sleep 3

echo ""
echo "═══════════════════════════════════════════════"
echo "  Estado de los servicios:"
echo "═══════════════════════════════════════════════"
for puerto in 5000 5001 5004 5005 5006 5007; do
    if ss -tlnp 2>/dev/null | grep -q ":$puerto "; then
        echo "  ✓ Puerto $puerto - ACTIVO"
    else
        echo "  ✗ Puerto $puerto - INACTIVO"
    fi
done
echo "═══════════════════════════════════════════════"
echo ""
echo "  App accesible en:"
echo "    → http://192.168.215.37:5000  (directo)"
echo "    → http://54.156.114.70:62001  (Apache proxy)"
echo ""
echo "  Logs en: /tmp/sabores_logs/"
echo "═══════════════════════════════════════════════"
