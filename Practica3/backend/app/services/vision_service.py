# Servicio de Computer Vision: preprocesamiento de imagenes para mejorar la precision del OCR
# Aplica un pipeline de tecnicas de vision artificial antes de pasar la imagen a EasyOCR

import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF: libreria para leer y convertir archivos PDF

def preprocesar_imagen(ruta: str, tipo: str) -> np.ndarray:
    # Punto de entrada: convierte el archivo (PDF o imagen) a un array numpy listo para OCR

    if tipo == "pdf":
        # Abre el PDF con PyMuPDF y renderiza la primera pagina a una imagen
        doc = fitz.open(ruta)
        page = doc[0]
        # Factor de escala 2x: duplica la resolucion de la imagen para mejorar el OCR
        # Una mayor resolucion permite que EasyOCR detecte texto pequeno con mas precision
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat)
        # Convierte los pixeles crudos del PDF a un array numpy de forma (alto, ancho, canales)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        # Algunos PDFs incluyen canal alfa (transparencia); se elimina para quedarse con RGB
        if pix.n == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    else:
        # Para imagenes JPG o PNG: abre con Pillow y convierte a RGB para consistencia
        img = Image.open(ruta).convert("RGB")
        img_array = np.array(img)

    # Aplica el pipeline de preprocesamiento de Computer Vision
    return _aplicar_preprocesamiento(img_array)

def _aplicar_preprocesamiento(img: np.ndarray) -> np.ndarray:
    # Pipeline de mejora de imagen en 4 pasos para optimizar la legibilidad del texto

    # Paso 1: Conversion a escala de grises
    # El OCR trabaja mejor con imagenes en blanco y negro; el color solo agrega ruido
    gris = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Paso 2: Redimensionamiento minimo
    # Si la imagen es muy pequena (menos de 800px de ancho), se escala con interpolacion cubica
    # para aumentar la resolucion sin perder nitidez en los bordes del texto
    h, w = gris.shape
    if w < 800:
        escala = 800 / w
        gris = cv2.resize(gris, None, fx=escala, fy=escala, interpolation=cv2.INTER_CUBIC)

    # Paso 3: Reduccion de ruido (denoising)
    # fastNlMeansDenoising elimina el ruido de la imagen preservando los bordes del texto
    # El parametro h=10 controla la intensidad del filtro
    gris = cv2.fastNlMeansDenoising(gris, h=10)

    # Paso 4: Umbralización adaptativa (binarizacion)
    # Convierte la imagen a blanco y negro puro usando un umbral local por region
    # ADAPTIVE_THRESH_GAUSSIAN_C ajusta el umbral segun el promedio ponderado del vecindario
    # Esto es superior al umbral global cuando la iluminacion es desigual en la imagen
    binaria = cv2.adaptiveThreshold(
        gris, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Paso 5: Correccion de inclinacion (deskew)
    # Detecta el angulo de inclinacion del texto usando el rectangulo minimo que encierra los pixeles oscuros
    # Si la inclinacion supera 0.5 grados, rota la imagen para enderezar el texto
    coords = np.column_stack(np.where(binaria < 128))
    if len(coords) > 0:
        angulo = cv2.minAreaRect(coords)[-1]
        if angulo < -45:
            angulo = 90 + angulo
        if abs(angulo) > 0.5:
            (h, w) = binaria.shape[:2]
            centro = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(centro, angulo, 1.0)
            # BORDER_REPLICATE rellena los bordes que quedan vacios tras la rotacion
            binaria = cv2.warpAffine(binaria, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    return binaria
