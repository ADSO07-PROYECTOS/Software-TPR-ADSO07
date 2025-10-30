"""
Script para verificar la conexión a la base de datos
Ejecuta: python test_conexion.py
"""
from app.conexion import verificar_conexion, obtener_conexion

print("=" * 50)
print("PRUEBA DE CONEXIÓN A LA BASE DE DATOS")
print("=" * 50)

# Test 1: Verificar conexión
print("\n📋 Test 1: Verificando conexión...")
if verificar_conexion():
    print("✅ Test 1 PASADO\n")
else:
    print("❌ Test 1 FALLIDO\n")
    exit(1)

# Test 2: Obtener conexión y hacer una consulta
print("📋 Test 2: Probando consulta a la base de datos...")
try:
    conexion = obtener_conexion()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        
        # Mostrar tablas
        cursor.execute("SHOW TABLES;")
        tablas = cursor.fetchall()
        
        print(f"✅ Tablas en la base de datos ({len(tablas)}):")
        for tabla in tablas:
            tabla_nombre = list(tabla.values())[0]
            print(f"   - {tabla_nombre}")
        
        cursor.close()
        conexion.close()
        print("\n✅ Test 2 PASADO")
    else:
        print("❌ No se pudo obtener conexión")
        exit(1)
        
except Exception as e:
    print(f"❌ Error durante la prueba: {e}")
    exit(1)

print("\n" + "=" * 50)
print("✅ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
print("=" * 50)
