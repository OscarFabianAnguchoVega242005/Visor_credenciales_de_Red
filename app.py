from flask import Flask, render_template
import subprocess
import re

app = Flask(__name__)

def obtener_todas_las_redes():
    redes_credenciales = []
    try:
        # 1. Obtener la lista de todos los perfiles de Wi-Fi guardados en Windows
        resultado_perfiles = subprocess.run(
            ['netsh', 'wlan', 'show', 'profiles'],
            capture_output=True, text=True, encoding='cp1252', errors='ignore'
        )
        
        # Filtrar los nombres de los perfiles usando expresiones regulares
        ssids = re.findall(r"(?:Perfil de todos los usuarios|All User Profile)\s*:\s*(.*)", resultado_perfiles.stdout)
        
        # 2. Por cada SSID encontrado, consultar su contraseña actual
        for ssid in ssids:
            ssid = ssid.strip()
            if not ssid:
                continue
                
            resultado_clave = subprocess.run(
                ['netsh', 'wlan', 'show', 'profile', f'name={ssid}', 'key=clear'],
                capture_output=True, text=True, encoding='cp1252', errors='ignore'
            )
            
            password = "No encontrada"
            for linea in resultado_clave.stdout.split('\n'):
                if "Contenido de la clave" in linea or "Key Content" in linea:
                    partes = linea.split(':')
                    if len(partes) > 1:
                        password = partes[1].strip()
                        break
            
            redes_credenciales.append({
                "ssid": ssid,
                "password": password
            })
            
    except Exception as e:
        print(f"Error procesando comandos netsh: {e}")
        
    return redes_credenciales

@app.route('/')
def index():
    # Escanea el sistema operativo antes de cargar la página
    datos_redes = obtener_todas_las_redes()
    return render_template('index.html', lista_redes=datos_redes)

if __name__ == '__main__':
    # Ejecuta el servidor local en el puerto 5000
    app.run(port=5000, debug=True)