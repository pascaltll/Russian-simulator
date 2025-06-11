# Usa una imagen base de Python oficial.
FROM python:3.12-slim-bookworm

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    openjdk-17-jre-headless \
    ffmpeg `# ¡Añade esta línea para instalar FFmpeg!` \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos de requisitos e instala las dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de tu aplicación al directorio de trabajo
COPY . .

# --- Inicio de los cambios para Whisper y permisos ---
# Crea el directorio de caché para Whisper (y otras librerías)
# Asegúrate de que tiene permisos de escritura para el usuario que se ejecuta
RUN mkdir -p /app/cache && \
    chmod -R 777 /app/cache

# Establece la variable de entorno XDG_CACHE_HOME para que Whisper sepa dónde guardar los modelos
ENV XDG_CACHE_HOME=/app/cache
# --- Fin de los cambios para Whisper y permisos ---

# Crea un directorio dedicado para los datos persistentes (incluyendo la base de datos)
RUN mkdir -p /app/database_volume_data && \
    chmod -R 777 /app/database_volume_data # Asegura permisos de escritura

# Expone el puerto en el que se ejecutará tu aplicación FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación usando Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]