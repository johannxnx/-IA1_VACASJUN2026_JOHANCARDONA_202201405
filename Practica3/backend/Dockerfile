# Pinear a Bookworm (Debian 12) porque Trixie (Debian 13) renombro paquetes que Playwright necesita
FROM python:3.11-slim-bookworm

# Dependencias del sistema: Tesseract para OCR, libgl1 para OpenCV headless (Debian Trixie+), wget para Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1 \
    libglib2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Instalar PyTorch CPU-only antes que EasyOCR para evitar descargar la version CUDA (~3GB innecesarios en servidor sin GPU)
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Instala el navegador Chromium y sus dependencias del sistema para el RPA con Playwright
RUN playwright install chromium --with-deps

# Pre-descarga los modelos de EasyOCR durante el build para evitar descarga en primer uso
# Sin esto, la primera solicitud OCR tardaria varios minutos descargando ~150MB
RUN python -c "import easyocr; easyocr.Reader(['es', 'en'], gpu=False)" 2>/dev/null || true

COPY . .

RUN mkdir -p uploads reports static

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
