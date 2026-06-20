# ============================================================
# prolog_interface.py — Conexion Python ↔ SWI-Prolog
#
# ESTE ES EL ARCHIVO MAS IMPORTANTE PARA LA DEFENSA.
# Aqui es donde Python se comunica con el motor de inferencia
# Prolog. No usamos pyswip porque es incompatible con
# SWI-Prolog 10.x. En su lugar llamamos directamente al
# ejecutable swipl usando subprocess.
#
# Flujo de una consulta:
#   1. Python construye un "goal" Prolog como string
#   2. subprocess lanza swipl con ese goal
#   3. Prolog ejecuta la inferencia y escribe JSON en stdout
#   4. Python lee stdout y parsea el JSON
# ============================================================

import subprocess
import json
from config import PROLOG_FILE

# SWI-Prolog necesita forward slashes en la ruta incluso en Windows.
# Si usamos backslashes, swipl no puede abrir el archivo.
_PROLOG_PATH = PROLOG_FILE.replace("\\", "/")


def _ejecutar_goal(goal):
    """
    Funcion privada que ejecuta un goal en SWI-Prolog via subprocess.

    Parametros:
        goal (str): Goal Prolog a ejecutar, ej: "cmd_sintomas"

    Retorna:
        str: Contenido de stdout de swipl (normalmente JSON)

    Lanza:
        RuntimeError: si swipl no esta instalado o el proceso falla
        subprocess.TimeoutExpired: si Prolog tarda mas de 30 segundos

    Ejemplo del comando que se ejecuta en terminal:
        swipl --quiet -g "consult('ruta/doctor_byte.pl'),cmd_sintomas,halt" -t "halt(1)"
    """
    cmd = [
        "swipl",
        "--quiet",           # Suprime el banner de bienvenida de SWI-Prolog
        "-g", f"consult('{_PROLOG_PATH}'),{goal},halt",
        #       ^--- carga el .pl    ^--- ejecuta el goal    ^--- termina normal
        "-t", "halt(1)"      # Si el goal FALLA, termina con codigo de salida 1
    ]

    # Ejecutamos swipl como proceso hijo, capturando su stdout y stderr
    resultado = subprocess.run(
        cmd,
        capture_output=True,  # captura stdout y stderr en variables
        text=True,             # decodifica bytes a string automaticamente
        encoding="utf-8",
        timeout=30             # maximo 30 segundos antes de matar el proceso
    )

    # Codigo 0 = goal exitoso, codigo 1 = goal fallo (sin datos)
    # Cualquier otro codigo indica error real del proceso
    if resultado.returncode not in (0, 1):
        raise RuntimeError(
            f"swipl termino con codigo {resultado.returncode}: {resultado.stderr.strip()}"
        )

    # Retornamos lo que Prolog escribio en stdout (el JSON)
    return resultado.stdout.strip()


def obtener_sintomas():
    """
    Consulta Prolog y retorna la lista completa de sintomas.

    Llama al predicado cmd_sintomas/0 definido en doctor_byte.pl,
    que usa findall/3 para recolectar todos los sintomas y los
    serializa como JSON en stdout.

    Retorna:
        list[dict]: Lista de dicts con "id" y "descripcion"
        Ejemplo: [{"id": "pantalla_negra", "descripcion": "La pantalla no muestra imagen..."}]
    """
    # Ejecutamos el predicado cmd_sintomas que esta definido en el .pl
    stdout = _ejecutar_goal("cmd_sintomas")

    # Si Prolog no escribio nada, retornamos lista vacia
    if not stdout:
        return []

    # Parseamos el JSON que Prolog escribio en stdout
    return json.loads(stdout)


def obtener_diagnostico(sintomas_usuario):
    """
    Recibe los sintomas seleccionados por el usuario y consulta Prolog
    para obtener los diagnosticos correspondientes.

    AQUI OCURRE LA INFERENCIA: Prolog unifica los sintomas con las
    reglas diagnosticar/1 y retorna todas las fallas que coinciden.

    Parametros:
        sintomas_usuario (list[str]): IDs de sintomas seleccionados
        Ejemplo: ["pantalla_negra", "ruido_disco"]

    Retorna:
        list[dict]: Lista de diagnosticos con falla, descripcion y recomendaciones
        Ejemplo: [{"falla": "fallo_disco_duro", "descripcion": "...", "recomendaciones": [...]}]
    """
    if not sintomas_usuario:
        return []

    # Construimos la lista en sintaxis Prolog: '[pantalla_negra,ruido_disco]'
    # Esta cadena se pasa como argumento al predicado cmd_diagnostico/1
    lista_atom = "[" + ",".join(sintomas_usuario) + "]"
    goal = f"cmd_diagnostico('{lista_atom}')"

    # Ejemplo del goal generado:
    # cmd_diagnostico('[pantalla_negra,ruido_disco]')

    stdout = _ejecutar_goal(goal)

    if not stdout:
        return []

    # Parseamos y retornamos la lista de diagnosticos en formato Python
    return json.loads(stdout)
