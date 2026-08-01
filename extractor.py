import subprocess
import os
import json
import re
import time

def get_direct_url(ok_url):
    """Extrae la URL directa del video usando yt-dlp"""
    try:
        cmd = ['yt-dlp', '--no-warnings', '--print', '%(url)s', ok_url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        return None

print("="*60)
print("🎬 EXTRACTOR - OKRU-PROMAX3")
print("="*60)

# 1. Verificar urls.txt
if not os.path.exists('urls.txt'):
    print("❌ No existe urls.txt")
    print("📝 Creando urls.txt vacío...")
    with open('urls.txt', 'w', encoding='utf-8') as f:
        f.write("[]")
    exit(0)

# 2. Leer JSON desde urls.txt
with open('urls.txt', 'r', encoding='utf-8') as f:
    contenido = f.read().strip()

if not contenido or contenido == "[]":
    print("ℹ️ urls.txt está vacío")
    exit(0)

try:
    peliculas = json.loads(contenido)
except json.JSONDecodeError:
    print("❌ urls.txt no contiene JSON válido")
    exit(0)

print(f"📥 {len(peliculas)} películas encontradas")

# 3. Procesar cada película
os.makedirs('peliculas', exist_ok=True)

peliculas_procesadas = 0
for pelicula in peliculas:
    titulo = pelicula.get('TITULO', 'Sin título')
    urls_okru = pelicula.get('URLS_OKRU', [])
    id_okru = pelicula.get('ID_OKRU')
    categoria = pelicula.get('CATEGORIA', 'GENERAL').upper()
    
    if not urls_okru:
        print(f"⚠️ {titulo} no tiene URLs")
        continue
    
    print(f"🔄 [{categoria}] {titulo} - ID: {id_okru}")
    
    # Extraer URL directa de la primera URL
    url_directa = get_direct_url(urls_okru[0])
    
    if url_directa:
        pelicula['URL_DIRECTA'] = url_directa
        print(f"   ✅ URL_DIRECTA obtenida")
    else:
        pelicula['URL_DIRECTA'] = ""
        print(f"   ❌ Falló la extracción")
    
    # Guardar en /peliculas
    json_path = os.path.join('peliculas', f'{categoria}.json')
    
    # Cargar JSON existente
    data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = []
    
    # Buscar por ID_OKRU o TMDB_ID
    encontrado = False
    for i, item in enumerate(data):
        if item.get('ID_OKRU') == id_okru or item.get('TMDB_ID') == pelicula.get('TMDB_ID'):
            data[i] = pelicula
            encontrado = True
            break
    
    if not encontrado:
        data.append(pelicula)
    
    # Guardar JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Guardado en {json_path}")
    peliculas_procesadas += 1
    time.sleep(0.5)

# 4. Limpiar urls.txt después de procesar
with open('urls.txt', 'w', encoding='utf-8') as f:
    f.write("[]")

print("\n🎉 Proceso completado")
print(f"📁 {peliculas_procesadas} películas procesadas")
print("🧹 urls.txt ha sido limpiado")
