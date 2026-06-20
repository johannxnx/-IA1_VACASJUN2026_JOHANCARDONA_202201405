# ============================================================
# history_manager.py — Gestion del historial de diagnosticos
#
# Persiste cada consulta realizada por el usuario en un
# archivo JSON (history.json). Este archivo esta en .gitignore
# porque contiene datos de sesion locales.
#
# Cada entrada del historial tiene:
#   - id:          UUID unico (para buscar entradas especificas)
#   - timestamp:   Fecha y hora en formato ISO 8601
#   - sintomas:    Lista de IDs de sintomas seleccionados
#   - diagnosticos: Lista de resultados de Prolog
#
# El historial se muestra en la seccion "Historial" del frontend,
# del mas reciente al mas antiguo.
# ============================================================

import json
import os
import uuid
from datetime import datetime
from config import HISTORY_FILE


def _inicializar_archivo():
    """
    Crea el archivo history.json y su directorio si no existen.
    Se llama antes de cada lectura para garantizar que el archivo existe.
    """
    directorio = os.path.dirname(HISTORY_FILE)
    os.makedirs(directorio, exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)  # inicia con lista vacia


def _leer_historial():
    """Lee el historial completo desde el archivo JSON."""
    _inicializar_archivo()
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _escribir_historial(datos):
    """Escribe el historial completo al archivo JSON."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def guardar_diagnostico(sintomas, diagnosticos):
    """
    Agrega una nueva entrada al historial.

    Parametros:
        sintomas     (list[str]):  IDs de sintomas seleccionados
        diagnosticos (list[dict]): Resultado del diagnostico de Prolog

    Retorna:
        dict: La entrada recien creada (con su id y timestamp)

    Se guarda siempre, incluso cuando diagnosticos esta vacio
    (el usuario selecciono sintomas pero Prolog no encontro ninguna falla).
    """
    historial = _leer_historial()

    entrada = {
        "id":          str(uuid.uuid4()),           # ID unico universal
        "timestamp":   datetime.now().isoformat(),  # "2026-06-19T14:30:00.000"
        "sintomas":    sintomas,
        "diagnosticos": diagnosticos
    }

    historial.append(entrada)
    _escribir_historial(historial)
    return entrada


def obtener_historial():
    """
    Retorna todos los diagnosticos guardados.
    La lista se invierte para mostrar el mas reciente primero.
    """
    historial = _leer_historial()
    return list(reversed(historial))


def obtener_entrada(entrada_id):
    """
    Busca y retorna una entrada especifica del historial por su UUID.

    Parametros:
        entrada_id (str): UUID de la entrada a buscar

    Retorna:
        dict | None: La entrada si existe, None si no se encuentra
    """
    historial = _leer_historial()
    for entrada in historial:
        if entrada["id"] == entrada_id:
            return entrada
    return None  # No encontrado
