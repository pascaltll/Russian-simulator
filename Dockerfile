# Usa una imagen base de Python ligera
FROM python:3.12-slim-buster

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia solo el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al contenedor
COPY . .

# Asegúrate de que Alembic pueda encontrar el entorno.
# Esto es crucial para las migraciones en Docker.
ENV PYTHONPATH=/app

# Exponer el puerto en el que la aplicación se ejecutará (Uvicorn por defecto es 8000)
EXPOSE 8000

# Comando para ejecutar la aplicación
# Puedes sobrescribir este en docker-compose.yml para las migraciones
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
