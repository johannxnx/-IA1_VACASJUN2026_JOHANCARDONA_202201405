import subprocess
import json
from config import PROLOG_FILE

# SWI-Prolog necesita forward slashes en la ruta incluso en Windows
_PROLOG_PATH = PROLOG_FILE.replace("\\", "/")


def _ejecutar_goal(goal):
    """
    Llama a swipl con un goal especifico y retorna el stdout como string.
    Si swipl no esta en el PATH o el goal falla, lanza una excepcion.
    """
    cmd = [
        "swipl",
        "--quiet",          # suprime mensajes de bienvenida
        "-g", f"consult('{_PROLOG_PATH}'),{goal},halt",
        "-t", "halt(1)"    # si el goal falla, termina con codigo 1
    ]

    resultado = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30
    )

    if resultado.returncode not in (0, 1):
        raise RuntimeError(
            f"swipl termino con codigo {resultado.returncode}: {resultado.stderr.strip()}"
        )

    return resultado.stdout.strip()


def obtener_sintomas():
    """
    Consulta Prolog y retorna todos los sintomas disponibles.
    Devuelve una lista de dicts: [{"id": "...", "descripcion": "..."}, ...]
    """
    stdout = _ejecutar_goal("cmd_sintomas")

    if not stdout:
        return []

    return json.loads(stdout)


def obtener_diagnostico(sintomas_usuario):
    """
    Recibe una lista de IDs de sintomas y consulta Prolog para diagnosticar.
    Devuelve una lista de dicts con falla, descripcion y recomendaciones.
    """
    if not sintomas_usuario:
        return []

    # Construye el atom Prolog: '[pantalla_negra,ruido_disco]'
    lista_atom = "[" + ",".join(sintomas_usuario) + "]"
    goal = f"cmd_diagnostico('{lista_atom}')"

    stdout = _ejecutar_goal(goal)

    if not stdout:
        return []

    return json.loads(stdout)
