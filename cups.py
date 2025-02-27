import subprocess

def encontrar_impresora_hp(modelo="LaserJet P4015n"):
    try:
        # Ejecutar el comando lpstat -v para listar impresoras
        resultado = subprocess.run(
            ["lpstat", "-v"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Buscar la línea que contiene el modelo de la impresora
        for linea in resultado.stdout.split('\n'):
            if modelo.lower() in linea.lower():
                # Extraer la dirección de la línea
                uri = linea.split(":")[1].strip()
                return uri
        
        return f"No se encontró la impresora {modelo}."
    
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar lpstat: {e}"
    except FileNotFoundError:
        return "El comando lpstat no está instalado. Instala CUPS con: sudo apt install cups"

# Ejecutar la función
direccion_impresora = encontrar_impresora_hp()
print("Dirección de la impresora:", direccion_impresora)