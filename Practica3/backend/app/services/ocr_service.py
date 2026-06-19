import re
import numpy as np
import easyocr
from datetime import date
from typing import Optional

_reader = None

def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["es", "en"], gpu=False)
    return _reader

def extraer_datos(imagen: np.ndarray) -> dict:
    reader = _get_reader()
    resultados = reader.readtext(imagen, detail=1)

    lineas = [texto for (_, texto, conf) in resultados if conf > 0.15]
    confianza_promedio = sum(float(conf) for (_, _, conf) in resultados) / len(resultados) if resultados else 0
    texto_completo = "\n".join(lineas)

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
    patrones = [
        # DTE guatemalteco: "Número de DTE: 29705968"
        (r"n[úu]mero\s+de\s+dte[:\s]*([A-Z0-9\-]+)", 1),
        # "Serie: DD77B4B4 Número de DTE: 29705968" → "DD77B4B4-29705968"
        (r"serie[:\s]*([A-Z0-9\-]+)\s+n[úu]mero\s+de\s+dte[:\s]*([A-Z0-9]+)", 2),
        # Código en esquina tipo "FAC-00001", "INV-2025-001"
        (r"\b((?:FAC|INV|FV|F)[A-Z0-9]*[-\/]\d{4,}(?:[-\/]\d+)?)\b", 1),
        # "Factura nº 1 2017" → "1/2017"
        (r"factura\s*n[°oºú\.]+\s*(\d{1,6})\s+(\d{4})", 0),
        # "Factura nº 1" / "Factura No. ABC-123"
        (r"(?:factura|invoice)[:\s#nNº°]*([A-Z0-9\-\/]{1,20})", 1),
        # "#123" genérico
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
                if val.upper() not in {"AUTORIZACIÓN", "AUTORIZACION", "NUMERO", "NÚMERO"}:
                    return val
    return None

# ---------------------------------------------------------------------------

_MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    # Abreviados (español e inglés)
    "ene": 1, "feb": 2, "mar": 3, "abr": 4,
    "may": 5, "jun": 6, "jul": 7, "ago": 8,
    "sep": 9, "oct": 10, "nov": 11, "dic": 12,
    "jan": 1, "apr": 4, "aug": 8,
}

def _extraer_fecha(texto: str) -> Optional[date]:
    # Formato con mes abreviado: "06-nov-2025" o "06/nov/2025"
    m = re.search(r"(\d{1,2})[/\-\.]([a-záéíóú]{2,9})[/\-\.](\d{4})", texto, re.IGNORECASE)
    if m:
        mes_num = _MESES.get(m.group(2).lower())
        if mes_num:
            try:
                return date(int(m.group(3)), mes_num, int(m.group(1)))
            except ValueError:
                pass

    # Formato numérico: "06-11-2025", "2025/11/06"
    patrones_num = [
        r"(\d{4})[/\-\.](\d{1,2})[/\-\.](\d{1,2})",
        r"(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})",
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

    # Fecha en texto: "31 de enero de 2017" / "al 31 de enero de 2017"
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
    excluir_kw = ["nit", "factura", "numero", "número", "fecha", "total", "serie",
                  "subtotal", "invoice", "cliente", "receptor", "comprador"]
    # Sufijos legales expandidos: S.A., S.L., S.L.N.E., S.L.U., S.Coop., S.R.L., LTDA, CIA, INC
    sufijos = (r"(?:S\.?\s*(?:A|L|R)\.?(?:\s*(?:N|U|E|R|L)\.?){0,2}"
               r"|S\.?\s*COOP\.?|LTDA?\.?|CIA\.?|INC\.?"
               r"|SOCIEDAD\s+AN[OÓ]NIMA|SOCIEDAD\s+LIMITADA)")

    # Prioridad 0: keyword "Proveedor:" exacto — busca en la misma línea
    # Si EasyOCR pone el nombre en la línea siguiente, lo busca en las líneas del documento
    lineas = texto.split("\n")
    for i, linea in enumerate(lineas):
        if re.match(r"proveedor\s*:", linea.strip(), re.IGNORECASE):
            # Intentar extraer del mismo texto de la línea después del ":"
            m = re.search(r"proveedor\s*:\s*(.+)", linea, re.IGNORECASE)
            if m:
                candidato = m.group(1).strip().rstrip(".,:")
                if len(candidato) > 3:
                    return candidato
            # Si la línea solo tiene "Proveedor:", tomar la siguiente línea no vacía
            for j in range(i + 1, min(i + 3, len(lineas))):
                siguiente = lineas[j].strip()
                if siguiente and not re.match(r"^(nit|fecha|cliente|dte|serie|nif|cif)\b", siguiente, re.IGNORECASE):
                    return siguiente.rstrip(".,:")
            break

    # Prioridad 1: keyword directo ("Nombre Emisor:", "Razón Social:", etc.)
    for patron in [
        r"(?:nombre\s+(?:del?\s+)?(?:emisor|proveedor|empresa)|raz[oó]n\s+social|emisor)[:\s]+([^\n]{3,80})",
        r"empresa[:\s]+([A-Z][^\n]{3,60})",
    ]:
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            nombre = m.group(1).strip().rstrip(".,")
            if not any(k in nombre.lower() for k in excluir_kw) and len(nombre) > 3:
                return nombre

    # Prioridad 2: texto en UNA SOLA línea que termina en sufijo legal
    # Nota: usamos [ ] (espacio literal) en vez de \s para NO cruzar saltos de línea
    for linea in texto.split("\n"):
        linea = linea.strip()
        m = re.search(rf"([A-Za-záéíóúñÁÉÍÓÚÑ][A-Za-záéíóúñÁÉÍÓÚÑ ,\.&]{{3,70}}{sufijos})",
                      linea, re.IGNORECASE)
        if m:
            nombre = m.group(0).strip().rstrip(".,")
            if not any(k in nombre.lower() for k in excluir_kw) and len(nombre) > 5:
                return nombre

    # Prioridad 3: primera línea completamente en mayúsculas que no sea encabezado ni código
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
    # Prioridad: NIT/NIF del emisor (no receptor)
    m = re.search(
        r"(?:nit|nif|cif|ruc)\s*(?:emisor|arrendador|vendedor)?[:/\s]+([0-9A-Z\-K]{6,15})",
        texto, re.IGNORECASE
    )
    return m.group(1).strip() if m else None

# ---------------------------------------------------------------------------

def _normalizar_monto(valor_str: str) -> Optional[float]:
    s = valor_str.strip()
    # Europeo: "1.100,50" (punto=miles, coma=decimal)
    if re.search(r'\d\.\d{3}', s) and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    elif re.search(r'\d\.\d{3}', s):
        # "1.100" sin coma → miles con punto, sin decimales
        s = s.replace('.', '')
    else:
        # Americano o simple: "1,100.50" o "4,364.00"
        s = s.replace(',', '')
    try:
        return round(float(s), 2)
    except ValueError:
        return None

def _extraer_monto(texto: str, palabras_clave: list) -> Optional[float]:
    for kw in palabras_clave:
        patron = rf"(?<![A-Za-z]){kw}[:\s\-]*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado is not None and resultado > 0:
                return resultado
    return None

def _extraer_total(texto: str) -> Optional[float]:
    # DTE guatemalteco: entre TOTALES e IVA puede haber varias líneas
    m = re.search(r"totales?([\s\S]{0,300})iva", texto, re.IGNORECASE)
    if m:
        seccion = m.group(1)
        numeros = re.findall(r"\d[\d\.,]*", seccion)
        for n in reversed(numeros):
            resultado = _normalizar_monto(n)
            if resultado and resultado > 0:
                return resultado

    # Formatos con etiqueta explícita y colon (evita capturar encabezados de columna como "Total\n3")
    for kw in ["total a ingresar", "monto total", "gran total", "amount due"]:
        patron = rf"(?<![A-Za-z]){kw}\s*:\s*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado and resultado > 0:
                return resultado

    # "TOTAL:" requiere el colon para no confundirse con la columna de tabla "Total"
    m = re.search(r"(?<![A-Za-z])total\s*:\s*[Q€$£]?\s*([\d\.,]+)", texto, re.IGNORECASE)
    if m:
        resultado = _normalizar_monto(m.group(1))
        if resultado and resultado > 0:
            return resultado
    return None

def _extraer_impuestos(texto: str) -> Optional[float]:
    # DTE: IVA dentro del bloque TOTALES
    m = re.search(r"totales?[\s\S]{0,300}iva[\s\n]+([\d\.,]+)", texto, re.IGNORECASE)
    if m:
        resultado = _normalizar_monto(m.group(1))
        if resultado and resultado > 0:
            return resultado

    # "IVA 12%: 642.75" o "IVA 129: 642.75" (OCR lee % como 9)
    # Patrón: IVA + porcentaje opcional (1-3 dígitos + % o :) + valor
    for kw in ["iva", "impuesto", "tax", "igv"]:
        patron = rf"(?<![A-Za-z]){kw}\s*(?:\d{{1,3}}[%:]{{0,2}}\s*)?\s*[Q€$£]?\s*([\d\.,]+)"
        m = re.search(patron, texto, re.IGNORECASE)
        if m:
            resultado = _normalizar_monto(m.group(1))
            if resultado and resultado > 0:
                return resultado
    return None
