import json
import os
import uuid
from datetime import datetime
from config import HISTORY_FILE


def _inicializar_archivo():
    """Crea el archivo de historial y su directorio si no existen."""
    directorio = os.path.dirname(HISTORY_FILE)
    os.makedirs(directorio, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def _leer_historial():
    _inicializar_archivo()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _escribir_historial(datos):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def guardar_diagnostico(sintomas, diagnosticos):
    """
    Guarda un nuevo diagnostico en el historial.
    Cada entrada tiene un ID unico, timestamp, sintomas usados y diagnosticos obtenidos.
    """
    historial = _leer_historial()

    entrada = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "sintomas": sintomas,
        "diagnosticos": diagnosticos
    }

    historial.append(entrada)
    _escribir_historial(historial)
    return entrada


def obtener_historial():
    """Devuelve todos los diagnosticos guardados, del mas reciente al mas antiguo."""
    historial = _leer_historial()
    return list(reversed(historial))


def obtener_entrada(entrada_id):
    """Busca y devuelve una entrada del historial por su ID. Devuelve None si no existe."""
    historial = _leer_historial()
    for entrada in historial:
        if entrada["id"] == entrada_id:
            return entrada
    return None
