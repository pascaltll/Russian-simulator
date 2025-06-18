# Usa una imagen base oficial de Python 3.12 slim
FROM python:3.12-slim-bookworm

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Actualiza pip a la última versión
RUN pip install --upgrade pip

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    openjdk-17-jre-headless \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copia el archivo de requerimientos antes para cachear instalación de dependencias
COPY requirements.txt .

# Instala PyTorch CPU, TorchAudio CPU y TorchVision CPU desde fuentes oficiales (sin '+cpu' en requirements.txt)
RUN pip install --no-cache-dir \
    torch==2.7.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir \
    torchvision==0.22.1 --index-url https://download.pytorch.org/whl/cpu

# Instala las demás dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación
COPY . .

# --- Configuración de caché y permisos ---

# Crea directorio de caché y otorga permisos totales para evitar problemas de escritura
RUN mkdir -p /app/cache && \
    chmod -R 777 /app/cache

# Establece variables de entorno para que las librerías usen /app/cache para caché
ENV XDG_CACHE_HOME=/app/cache
ENV LANGUAGE_TOOL_PYTHON_CACHE_DIR=/app/cache

# Crea directorio para datos persistentes (base de datos, etc.) y da permisos
RUN mkdir -p /app/database_volume_data && \
    chmod -R 777 /app/database_volume_data

# Expone el puerto donde corre FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
