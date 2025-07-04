# Usa una imagen base de Python oficial y delgada (basada en Debian)
# Es más compatible con librerías que necesitan compilación que Alpine.
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala dependencias del sistema necesarias para compilar tgcrypto y pillow
# --no-install-recommends mantiene la imagen pequeña
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia solo el archivo de requerimientos primero para aprovechar el caché de Docker
COPY src/requirements.txt .

# Instala las dependencias de Python
# Usamos las comillas en 'pyrogram[fast]' por si acaso
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código de la aplicación
COPY ./src .

# El comando que se ejecutará cuando el contenedor inicie
CMD ["python", "gemini.py"]