import os
import re

def extract_imports_from_file(file_path):
    """
    Extrae los nombres de paquetes de alto nivel de las declaraciones
    'import' y 'from ... import' en un archivo Python.
    """
    imports = set()
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Ignorar líneas de comentarios y líneas vacías
                line = line.split('#', 1)[0].strip()
                if not line:
                    continue

                # Expresión regular para encontrar 'import paquete' o 'from paquete import ...'
                # Captura el nombre del paquete que sigue a 'import' o 'from'
                match = re.match(r"^(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_.]+)", line)
                if match:
                    full_import_name = match.group(1)
                    # Solo nos interesa el nombre del paquete de más alto nivel
                    # Ejemplo: 'fastapi.responses' -> 'fastapi'
                    top_level_package = full_import_name.split('.')[0]
                    imports.add(top_level_package)
    except Exception as e:
        print(f"Error procesando el archivo {file_path}: {e}")
    return imports

def find_all_python_imports(root_directory):
    """
    Recorre un directorio y sus subdirectorios para encontrar todos los archivos .py
    y extraer las dependencias de importación únicas de alto nivel.
    """
    all_unique_imports = set()
    # Lista de directorios a ignorar (comunes para entornos virtuales, caches, etc.)
    exclude_dirs = {'venv', '.venv', '__pycache__', 'env', '.git', 'alembic'}

    for dirpath, dirnames, filenames in os.walk(root_directory):
        # Modificar dirnames en el lugar para que os.walk ignore estos directorios
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        for filename in filenames:
            if filename.endswith('.py'):
                file_path = os.path.join(dirpath, filename)
                print(f"Analizando: {file_path}") # Para seguimiento
                current_file_imports = extract_imports_from_file(file_path)
                all_unique_imports.update(current_file_imports)

    return sorted(list(all_unique_imports)) # Retorna una lista ordenada

if __name__ == "__main__":
    # La ruta del directorio raíz de tu proyecto.
    # os.getcwd() obtendrá el directorio desde donde ejecutas el script.
    # Asegúrate de ejecutar este script desde la raíz de tu proyecto.
    project_root_dir = os.getcwd()

    print(f"Iniciando escaneo de archivos .py en: {project_root_dir}\n")

    detected_dependencies = find_all_python_imports(project_root_dir)

    print("\n--- Dependencias de Python de alto nivel detectadas ---")
    print("-----------------------------------------------------")
    for dep in detected_dependencies:
        print(dep)
    print("-----------------------------------------------------")
    print("\nNotas importantes para tu requirements.txt:")
    print("1. Esta lista incluye TODAS las importaciones de alto nivel.")
    print("2. Debes filtrar manualmente los módulos de la librería estándar de Python (ej: os, sys, json, re, logging, typing, etc.).")
    print("3. También debes filtrar los módulos que forman parte de tu propio proyecto (tus propios archivos .py y paquetes locales).")
    print("4. Para las dependencias externas, es una buena práctica especificar una versión (ej: requests==2.32.3).")
    print("5. Considera usar 'pip-tools' (pip-compile) para gestionar tus dependencias de forma más robusta.")
    