import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF

def preprocesar_imagen(ruta: str, tipo: str) -> np.ndarray:
    """Convierte PDF o imagen a array numpy preprocesado para OCR."""
    if tipo == "pdf":
        doc = fitz.open(ruta)
        page = doc[0]
        mat = fitz.Matrix(2.0, 2.0)  # escala 2x para mejor OCR
        pix = page.get_pixmap(matrix=mat)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    else:
        img = Image.open(ruta).convert("RGB")
        img_array = np.array(img)

    return _aplicar_preprocesamiento(img_array)

def _aplicar_preprocesamiento(img: np.ndarray) -> np.ndarray:
    """Pipeline de Computer Vision para mejorar calidad de imagen para OCR."""
    # Convertir a escala de grises
    gris = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Redimensionar si es muy pequeña
    h, w = gris.shape
    if w < 800:
        escala = 800 / w
        gris = cv2.resize(gris, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)

    # Reducción de ruido
    gris = cv2.fastNlMeansDenoising(gris, h=10)

    # Umbralización adaptativa (binarización)
    binaria = cv2.adaptiveThreshold(
        gris, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Corrección de inclinación (deskew)
    coords = np.column_stack(np.where(binaria < 128))
    if len(coords) > 0:
        angulo = cv2.minAreaRect(coords)[-1]
        if angulo < -45:
            angulo = 90 + angulo
        if abs(angulo) > 0.5:
            (h, w) = binaria.shape[:2]
            centro = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(centro, angulo, 1.0)
            binaria = cv2.warpAffine(binaria, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return binaria
