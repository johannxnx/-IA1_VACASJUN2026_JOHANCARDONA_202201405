# Servicio OCR: extraccion de campos estructurados desde texto reconocido por EasyOCR
# Maneja multiples formatos de factura: DTE Guatemala, facturas academicas y documentos espanoles

import re
import numpy as np
import easyocr
from datetime import date
from typing import Optional

# Variable global para reutilizar el lector OCR entre peticiones
# La inicializacion es costosa (carga modelos de red neuronal), por eso se hace una sola vez
_reader = None

def _get_reader():
    # Patron Singleton: crea el lector solo la primera vez que se necesita
    global _reader
    if _reader is None:
        # Carga los modelos de EasyOCR para espanol e ingles, usando CPU (sin GPU disponible)
        _reader = easyocr.Reader(["es", "en"], gpu=False)
    return _reader

def extraer_datos(imagen: np.ndarray) -> dict:
    # Funcion principal: recibe la imagen preprocesada y retorna un diccionario con todos los campos
    reader = _get_reader()

    # detail=1 retorna cada bloque de texto con su posicion y nivel de confianza
    resultados = reader.readtext(imagen, detail=1)

    # Filtra bloques con confianza mayor a 15% para descartar texto ilegible
    # Se uso 0.15 en lugar de 0.30 porque facturas con colores (DTE) tienen confianza baja en encabezados
    lineas = [texto for (_, texto, conf) in resultados if conf > 0.15]

    # Calcula la confianza promedio del documento completo como indicador de calidad de lectura
    confianza_promedio = sum(float(conf) for (_, _, conf) in resultados) / len(resultados) if resultados else 0

    # Une todas las lineas en un solo texto para facilitar las busquedas con regex
    texto_completo = "\n".join(lineas)

    # Extrae cada campo usando patrones regex especializados por tipo de dato
    subtotal = _extraer_monto(texto_completo, ["subtotal", "sub total", "sub-total"])
    impuestos = _extraer_impuestos(texto_completo)
    total = _extraer_total(texto_completo)

    return {
        "texto_crudo": texto_completo,
        "confianza": float(round(confianza_promedio * 100, 2)),
        "numero_factura": _extraer_numero_factura(texto_completo),
        "fecha_factura": _extraer_fecha(texto_completo),
        "nombre_proveedor": _extraer_nombre_proveedor(texto_completo),
        "nit": _extraer_nit(texto_completo),
        "subtotal": subtotal,
        "impuestos": impuestos,
        "total": total,
    }

# ---------------------------------------------------------------------------

def _extraer_numero_factura(texto: str) -> Optional[str]:
    # Intenta varios patrones de numero de factura en orden de especificidad
    patrones = [
        # DTE guatemalteco: "Numero de DTE: 29705968"
        (r"n[úu]mero\s+de\s+dte[:\s]*([A-Z0-9\-]+)", 1),
        # Factura con serie y numero DTE: "Serie: DD77B4B4 Numero de DTE: 29705968" -> "DD77B4B4-29705968"
        (r"serie[:\s]*([A-Z0-9\-]+)\s+n[úu]mero\s+de\s+dte[:\s]*([A-Z0-9]+)", 2),
        # Codigos en esquina superior: "FAC-00001", "INV-2025-001"
        (r"\b((?:FAC|INV|FV|F)[A-Z0-9]*[-\/]\d{4,}(?:[-\/]\d+)?)\b", 1),
        # Factura con numero y anio: "Factura n 1 2017" -> "1/2017"
        (r"factura\s*n[°oºú\.]+\s*(\d{1,6})\s+(\d{4})", 0),
        # Patron generico: "Factura No. ABC-123"
        (r"(?:factura|invoice)[:\s#nNº°]*([A-Z0-9\-\/]{1,20})", 1),
        # Numero con prefijo: "#123456"
        (r"[#N°]\s*([0-9]{4,15})", 1),
    ]
    for patron, modo in patrones:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            if modo == 2:
                return f"{m.group(1)}-{m.group(2)}"
            elif modo == 0:
                return f"{m.group(1)}/{m.group(2)}"
            else:
                val = m.group(1).strip()
                # Descarta falsos positivos como palabras clave del documento
                if val.upper() not in {"AUTORIZACION", "AUTORIZACION", "NUMERO", "NUMERO"}:
                    return val
    return None

# ---------------------------------------------------------------------------

# Diccionario para convertir nombres de meses en espanol e ingles a su numero
_MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    "jan": 1, "apr": 4, "aug": 8,
}

def _extraer_fecha(texto: str) -> Optional[date]:
    # Intenta detectar fechas en multiples formatos escritos en facturas reales

    # Formato con mes abreviado: "06-nov-2025" o "06/nov/2025"
    m = re.search(r"(\d{1,2})[/\-\.]([a-záéíóú]{2,9})[/\-\.](\d{4})", texto, re.IGNORECASE)
    if m:
        mes_num = _MESES.get(m.group(2).lower())
        if mes_num:
            try:
                return date(int(m.group(3)), mes_num, int(m.group(1)))
            except ValueError:
                pass

    # Formato numerico: "2025/11/06" (ISO) o "06-11-2025" (europeo)
    patrones_num = [
        r"(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})",    # ISO: anio-mes-dia
        r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})",   # Europeo: dia-mes-anio
    ]
    for p in patrones_num:
        m = re.search(p, texto)
        if m:
            g = m.groups()
            try:
                if len(g[0]) == 4:
                    return date(int(g[0]), int(g[1]), int(g[2]))
                else:
                    anio = int(g[2]) if len(g[2]) == 4 else 2000 + int(g[2])
                    return date(anio, int(g[1]), int(g[0]))
            except ValueError:
                continue

    # Fecha en texto narrativo: "31 de enero de 2017" o "al 31 de enero de 2017"
    m = re.search(r"(?:al\s+)?(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})", texto, re.IGNORECASE)
    if m:
        mes_num = _MESES.get(m.group(2).lower())
        if mes_num:
            try:
                return date(int(m.group(3)), mes_num, int(m.group(1)))
            except ValueError:
                pass
    return None

# ---------------------------------------------------------------------------

def _extraer_nombre_proveedor(texto: str) -> Optional[str]:
    # Palabras clave que NO deben aparecer en el nombre del proveedor (evitar falsos positivos)
    excluir_kw = ["nit", "factura", "numero", "número", "fecha", "total", "serie",
                  "subtotal", "invoice", "cliente", "receptor", "comprador"]

    # Patron de sufijos legales para identificar nombres de empresas en el texto
    # Incluye: S.A., S.L., S.L.N.E., S.L.U., S.Coop., S.R.L., LTDA, CIA, INC, SOCIEDAD ANONIMA
    sufijos = (r"(?:S\.?\s*(?:A|L|R)\.?(?:\s*(?:N|U|E|R|L)\.?){0,2}"
               r"|S\.?\s*COOP\.?|LTDA?\.?|CIA\.?|INC\.?"
               r"|SOCIEDAD\s+AN[OÓ]NIMA|SOCIEDAD\s+LIMITADA)")

    # Prioridad 0: busca la etiqueta "Proveedor:" y extrae el nombre de la misma linea o la siguiente
    # EasyOCR a veces pone el valor en la siguiente linea al separar por bloques
    lineas = texto.split("\n")
    for i, linea in enumerate(lineas):
        if re.match(r"proveedor\s*:", linea.strip(), re.IGNORECASE):
            m = re.search(r"proveedor\s*:\s*(.+)", linea, re.IGNORECASE)
            if m:
                candidato = m.group(1).strip().rstrip(".,:")
                if len(candidato) > 3:
                    return candidato
            # Si la linea solo dice "Proveedor:", toma la siguiente linea no vacia como nombre
            for j in range(i + 1, min(i + 3, len(lineas))):
                siguiente = lineas[j].strip()
                if siguiente and not re.match(r"^(nit|fecha|cliente|dte|serie|nif|cif)\b", siguiente, re.IGNORECASE):
                    return siguiente.rstrip(".,:")
            break

    # Prioridad 1: etiquetas directas como "Nombre Emisor:", "Razon Social:", "Emisor:"
    for patron in [
        r"(?:nombre\s+(?:del?\s+)?(?:emisor|proveedor|empresa)|raz[oó]n\s+social|emisor)[:\s]+([^\n]{3,80})",
        r"empresa[:\s]+([A-Z][^\n]{3,60})",
    ]:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            nombre = m.group(1).strip().rstrip(".,")
            if not any(k in nombre.lower() for k in excluir_kw) and len(nombre) > 3:
                return nombre

    # Prioridad 2: lineas que terminan en sufijo legal (S.A., LTDA, etc.)
    # Se busca linea por linea para evitar que el patron cruce saltos de linea
    for linea in texto.split("\n"):
        linea = linea.strip()
        m = re.search(rf"([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ ,\.&]{{3,70}}{sufijos})",
                      linea, re.IGNORECASE)
        if m:
            nombre = m.group(0).strip().rstrip(".,")
            if not any(k in nombre.lower() for k in excluir_kw) and len(nombre) > 5:
                return nombre

    # Prioridad 3: primera linea completamente en mayusculas que no sea un codigo ni encabezado
    # Muchas facturas imprimen el nombre de la empresa en mayusculas en la parte superior
    for linea in texto.split("\n"):
        linea = linea.strip()
        if (len(linea) > 8
                and linea.isupper()
                and not re.search(r'^[A-Z]{2,6}[-/]\d', linea)
                and not any(k in linea.lower() for k in excluir_kw)):
            return linea

    return None

# ---------------------------------------------------------------------------

def _extraer_nit(texto: str) -> Optional[str]:
    # Busca el NIT del emisor o vendedor, priorizando etiquetas que lo identifiquen como proveedor
    m = re.search(
        r"(?:nit|nif|cif|ruc)\s*(?:emisor|arrendador|vendedor)?[:/\s]+([0-9A-Z\-K]{6,15})",
        texto, re.IGNORECASE
    )
    return m.group(1).strip() if m else None

# ---------------------------------------------------------------------------

def _normalizar_monto(valor_str: str) -> Optional[float]:
    # Convierte una cadena de monto a float, manejando formatos europeo y americano:
    # Europeo: "1.100,50" (punto = separador de miles, coma = decimal)
    # Americano: "1,100.50" (coma = separador de miles, punto = decimal)
    s = valor_str.strip()
    if re.search(r'\d\.\d{3}', s) and ',' in s:
        # Formato europeo: elimina puntos de miles y convierte coma decimal a punto
        s = s.replace('.', '').replace(',', '.')
    elif re.search(r'\d\.\d{3}', s):
        # Numero con punto de miles sin decimales: "1.100" -> 1100
        s = s.replace('.', '')
    else:
        # Formato americano o simple: elimina comas de miles
        s = s.replace(',', '')
    try:
        return round(float(s), 2)
    except ValueError:
        return None

def _extraer_monto(texto: str, palabras_clave: list) -> Optional[float]:
    # Extrae un monto numerico precedido por alguna de las palabras clave dadas
    for kw in palabras_clave:
        patron = rf"(?<![A-Za-z]){kw}[:\s\-]*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado is not None and resultado > 0:
                return resultado
    return None

def _extraer_total(texto: str) -> Optional[float]:
    # Estrategia 1: DTE guatemalteco tiene la estructura "TOTALES ... IVA"
    # El total aparece como el ultimo numero positivo entre esas dos palabras
    m = re.search(r"totales?([\s\S]{0,300})iva", texto, re.IGNORECASE)
    if m:
        seccion = m.group(1)
        numeros = re.findall(r"\d[\d\.,]*", seccion)
        for n in reversed(numeros):
            resultado = _normalizar_monto(n)
            if resultado and resultado > 0:
                return resultado

    # Estrategia 2: etiquetas explicitas con colon para formatos mas elaborados
    for kw in ["total a ingresar", "monto total", "gran total", "amount due"]:
        patron = rf"(?<![A-Za-z]){kw}\s*:\s*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado and resultado > 0:
                return resultado

    # Estrategia 3: "TOTAL:" con colon obligatorio
    # El colon es importante para no confundir con encabezados de columna como "Total" en tablas
    m = re.search(r"(?<![A-Za-z])total\s*:\s*[Q€$£]?\s*([\d\.,]+)", texto, re.IGNORECASE)
    if m:
        resultado = _normalizar_monto(m.group(1))
        if resultado and resultado > 0:
            return resultado
    return None

def _extraer_impuestos(texto: str) -> Optional[float]:
    # Estrategia 1: DTE guatemalteco, IVA dentro del bloque TOTALES
    # Busca el valor numerico inmediatamente despues de "iva" en esa seccion
    m = re.search(r"totales?[\s\S]{0,300}iva[\s\n]+([\d\.,]+)", texto, re.IGNORECASE)
    if m:
        resultado = _normalizar_monto(m.group(1))
        if resultado and resultado > 0:
            return resultado

    # Estrategia 2: patron generico "IVA 12%: 642.75" o "IVA 129: 642.75"
    # El grupo de porcentaje (1-3 digitos + %) es opcional para manejar variantes del OCR
    for kw in ["iva", "impuesto", "tax", "igv"]:
        patron = rf"(?<![A-Za-z]){kw}\s*(?:\d{{1,3}}[%:]{{0,2}}\s*)?\s*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado and resultado > 0:
                return resultado
    return None
