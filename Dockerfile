# Usa una imagen base de Python oficial.
# Recomendado: python:3.12-slim-bookworm para un tamaño de imagen más pequeño.
FROM python:3.12-slim-bookworm

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias para algunas librerías Python y Java para LanguageTool.
RUN apt-get update && apt-get install -y \
    build-essential \
    openjdk-17-jre-headless \
    # Si tienes otras dependencias que requieran compilación (ej. cryptography), podrían necesitar gcc
    # pero para sqlite3 puro no es estrictamente necesario, aunque build-essential lo incluye.
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos e instala las dependencias de Python
# Esto se hace primero para aprovechar el cache de Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo
COPY . .

# Crea el directorio de la base de datos si aún no existe, para asegurar que el volumen lo pueda montar.
# Esto es opcional, pero ayuda a evitar problemas de permisos con el volumen.
# Asumo que app.db estará en la raíz de /app, o un subdirectorio si lo configuras.
# Si tu app.db no está en la raíz, ajusta la ruta.
# Por ejemplo, si está en /app/data/app.db, crearías RUN mkdir -p /app/data
RUN mkdir -p /app/database_volume_data # Un directorio para los datos persistentes si app.db está dentro

# Expone el puerto en el que se ejecutará tu aplicación FastAPI (por defecto Uvicorn es 8000)
EXPOSE 8000

# Comando para iniciar la aplicación usando Uvicorn
# La opción --host 0.0.0.0 es crucial para que la aplicación sea accesible desde fuera del contenedor.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]