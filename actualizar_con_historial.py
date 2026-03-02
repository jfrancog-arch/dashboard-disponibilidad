"""
Actualizador de Dashboard Loggro con Historial Automático
Genera dashboard con filtros por periodo y descarga CSV
Compatible con GitHub Pages y SharePoint (via embed)
"""

from datetime import datetime
import json
import os
import re

# ============================================================
# CONFIGURACIÓN
# ============================================================

LOGO_URL = "https://tuloggro.sharepoint.com/Shared%20Documents/KIT%20DE%20MEDIOS%20NUEVA%20MARCA/Logo%20Loggro.png"

PRODUCT_COLORS = {
    "ERP": "#e55e1e",
    "Nómina": "#c9d52a",
    "Alojamientos": "#149e71",
    "Restobar": "#dd1c4b",
    "POS Tienda": "#064f8f",
    "Sesiones Masivas": "#7b68ee"
}

PRODUCT_URLS = {
    "ERP": "https://meetings.hubspot.com/loggro/rotacion-erp",
    "Nómina": "https://meetings.hubspot.com/loggro/nomina",
    "Restobar": "https://meetings.hubspot.com/loggro/restobar",
    "Alojamientos": "https://meetings.hubspot.com/loggro/alojamientos",
    "POS Tienda": "https://meetings.hubspot.com/loggro/pos-tienda",
    "Sesiones Masivas": "https://tuloggro.sharepoint.com/:u:/s/FormacionLoggro/EWtHzF6XsJpGtymdOR3g4WQBfGauF7CZ431Qomk5scxX2g?e=F0tnZk"
}

PRODUCT_CSS_CLASS = {
    "ERP": "erp",
    "Nómina": "nomina",
    "Alojamientos": "alojamientos",
    "Restobar": "restobar",
    "POS Tienda": "pos",
    "Sesiones Masivas": "masivas"
}

HISTORIAL_FILE = "historial.json"

# ============================================================
# FUNCIONES DE HISTORIAL
# ============================================================

def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        try:
            with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_historial(historial):
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

def agregar_al_historial(datos):
    historial = cargar_historial()
    fecha_actual = datetime.now().strftime('%d/%m/%Y')
    
    for item in datos:
        if not item.get('es_masivas', False):
            registro = {
                "fecha": fecha_actual,
                "producto": item['producto'],
                "dias": item['dias'],
                "fecha_disponible": item['fecha']
            }
            historial.append(registro)
    
    guardar_historial(historial)
    print(f"\n✅ Historial actualizado: {len(historial)} registros totales")
    return historial

# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def solicitar_datos():
    productos = ["ERP", "Nómina", "Restobar", "Alojamientos", "POS Tienda"]
    datos = []
    
    print("\n" + "="*70)
    print("  📅 ACTUALIZADOR DE DASHBOARD CON HISTORIAL - LOGGRO")
    print("="*70)
    print("\nIngresa los datos de disponibilidad para cada producto")
    print("Formato de fecha: DD/MM/AAAA (ejemplo: 20/02/2026)\n")
    
    for producto in productos:
        color = PRODUCT_COLORS[producto]
        print(f"\n{'─'*70}")
        print(f"🔹 {producto.upper()} (Color: {color})")
        print(f"{'─'*70}")
        
        while True:
            fecha = input("  📅 Próxima fecha disponible (DD/MM/AAAA): ").strip()
            if "/" in fecha and len(fecha) == 10:
                break
            print("  ⚠️  Formato incorrecto. Usa DD/MM/AAAA")
        
        while True:
            try:
                dias = int(input("  ⏱️  Días de espera: ").strip())
                if dias >= 0: break
                print("  ⚠️  Debe ser un número positivo")
            except ValueError:
                print("  ⚠️  Debe ser un número entero")
        
        datos.append({
            "producto": producto,
            "fecha": fecha,
            "dias": dias,
            "url": PRODUCT_URLS[producto],
            "css_class": PRODUCT_CSS_CLASS[producto],
            "es_masivas": False
        })
    
    print(f"\n{'─'*70}")
    print("✅ Sesiones Masivas se agregará automáticamente")
    print(f"{'─'*70}")
    
    datos.append({
        "producto": "Sesiones Masivas",
        "fecha": None,
        "dias": None,
        "url": PRODUCT_URLS["Sesiones Masivas"],
        "css_class": PRODUCT_CSS_CLASS["Sesiones Masivas"],
        "es_masivas": True
    })
    
    return datos

# ============================================================
# GENERACIÓN DE DASHBOARD
# ============================================================

def generar_datos_js(datos, historial):
    current_data_js = "const currentData = " + json.dumps([
        {
            "producto": item["producto"],
            "fecha": item["fecha"],
            "dias": item["dias"],
            "url": item["url"],
            "css_class": item["css_class"],
            "es_masivas": item.get("es_masivas", False)
        }
        for item in datos
    ], ensure_ascii=False, indent=4) + ";"
    
    historical_data_js = "\nconst historicalData = " + json.dumps(historial, ensure_ascii=False, indent=4) + ";"
    
    return current_data_js + historical_data_js

def generar_dashboard(datos, historial):
    productos = [d for d in datos if not d.get('es_masivas')]
    masivas = [d for d in datos if d.get('es_masivas')]
    productos_ordenados = sorted(productos, key=lambda x: x['dias'])
    datos_ordenados = productos_ordenados + masivas
    
    datos_js = generar_datos_js(datos_ordenados, historial)
    
    # Buscar template
    template_path = None
    for path in ['index.html', 'dashboard_con_historial.html']:
        if os.path.exists(path):
            template_path = path
            break
    
    if template_path:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        pattern = r'const currentData = \[.*?\];.*?const historicalData = \[.*?\];'
        html_content = re.sub(pattern, datos_js, html_content, flags=re.DOTALL)
        
        html_content = re.sub(
            r'https://tuloggro\.sharepoint\.com/[^"]*[Ll]ogo[^"]*\.png',
            LOGO_URL,
            html_content
        )
    else:
        print("⚠️  Template no encontrado (index.html o dashboard_con_historial.html)")
        return
    
    # Guardar ambos archivos
    for filename in ['dashboard_sharepoint.html', 'index.html']:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    print("\n" + "="*70)
    print("✅ ¡DASHBOARD GENERADO EXITOSAMENTE!")
    print("="*70)
    print(f"\n📄 Archivos: dashboard_sharepoint.html + index.html")
    print(f"📅 Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"📊 Productos: {len(productos)} + Sesiones Masivas")
    print(f"📈 Registros históricos: {len(historial)}")
    print("\n📋 Para subir a GitHub:")
    print("   git add -A")
    print('   git commit -m "Actualizar disponibilidad"')
    print("   git push")
    print("="*70 + "\n")

def main():
    print("\n╔" + "═"*68 + "╗")
    print("║" + " "*15 + "DASHBOARD LOGGRO CON HISTORIAL" + " "*23 + "║")
    print("╚" + "═"*68 + "╝")
    
    datos = solicitar_datos()
    
    print("\n🔄 Guardando en historial...")
    historial = agregar_al_historial(datos)
    
    print("\n🔄 Generando dashboard HTML con historial...")
    generar_dashboard(datos, historial)
    
    input("\n✨ Presiona Enter para salir...")

if __name__ == "__main__":
    main()
