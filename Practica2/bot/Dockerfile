# Imagen base: Python 3.11 en su versión "slim" (sin paquetes extra del SO, más ligera)
FROM python:3.11-slim

# Establece /app como directorio de trabajo dentro del contenedor
# Todos los comandos siguientes se ejecutan desde aquí
WORKDIR /app

# Copia SOLO el archivo de dependencias primero (antes del resto del código)
# Esto aprovecha la caché de Docker: si requirements.txt no cambia,
# Docker no reinstala los paquetes en cada build, ahorrando tiempo
COPY requirements.txt .

# Instala las dependencias de Python listadas en requirements.txt
# --no-cache-dir evita guardar caché de pip dentro de la imagen (reduce el tamaño final)
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el resto del código fuente al directorio de trabajo (/app)
COPY . .

# Comando que se ejecuta al iniciar el contenedor
# Lanza directamente el script del bot con Python
# El bot usa polling (consulta activa a Telegram) en lugar de webhooks
CMD ["python", "bot.py"]
