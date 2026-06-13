import json
import os
from config import BASE_DIR, PROLOG_FILE

SYMPTOMS_FILE    = os.path.join(BASE_DIR, "data", "symptoms.json")
FAULTS_FILE      = os.path.join(BASE_DIR, "data", "faults.json")
RECS_FILE        = os.path.join(BASE_DIR, "data", "recommendations.json")
RULES_FILE       = os.path.join(BASE_DIR, "data", "rules.json")


def _leer(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _escapar_atom(texto):
    """Envuelve el texto en comillas simples escapando las internas."""
    return "'" + texto.replace("'", "\\'") + "'"


def generar_pl():
    """
    Regenera el archivo doctor_byte.pl completo a partir de los JSON de datos.
    Se llama cada vez que el admin modifica sintomas, fallas, recomendaciones o reglas.
    """
    sintomas  = _leer(SYMPTOMS_FILE)
    fallas    = _leer(FAULTS_FILE)
    recs      = _leer(RECS_FILE)
    reglas    = _leer(RULES_FILE)

    lineas = []

    lineas.append("% ============================================================")
    lineas.append("% Doctor Byte - Base de Conocimiento (generado por el admin)")
    lineas.append("% Inteligencia Artificial 1 - USAC 2026")
    lineas.append("% ============================================================")
    lineas.append("")
    lineas.append(":- dynamic tiene_sintoma/1.")
    lineas.append("")

    # --- SINTOMAS ---
    lineas.append("% --- Sintomas ---")
    for s in sintomas:
        lineas.append(f"sintoma({s['id']}).")
    lineas.append("")

    lineas.append("% --- Descripciones de sintomas ---")
    for s in sintomas:
        lineas.append(f"descripcion_sintoma({s['id']}, {_escapar_atom(s['descripcion'])}).")
    lineas.append("")

    # --- FALLAS ---
    lineas.append("% --- Fallas ---")
    for f in fallas:
        lineas.append(f"falla({f['id']}).")
    lineas.append("")

    lineas.append("% --- Descripciones de fallas ---")
    for f in fallas:
        lineas.append(f"descripcion_falla({f['id']}, {_escapar_atom(f['descripcion'])}).")
    lineas.append("")

    # --- RECOMENDACIONES ---
    lineas.append("% --- Recomendaciones ---")
    for fault_id, lista in recs.items():
        items = ", ".join(_escapar_atom(r) for r in lista)
        lineas.append(f"recomendaciones({fault_id}, [{items}]).")
    lineas.append("")

    # --- REGLAS DE INFERENCIA ---
    lineas.append("% --- Reglas de inferencia ---")
    for r in reglas:
        condiciones = ",\n    ".join(f"tiene_sintoma({c})" for c in r["conditions"])
        lineas.append(f"diagnosticar({r['conclusion']}) :-")
        lineas.append(f"    {condiciones}.")
    lineas.append("")

    # --- PREDICADOS ESTATICOS (infraestructura, no cambian) ---
    lineas.append("% --- Predicados auxiliares ---")
    lineas.append("")
    lineas.append("cargar_sintomas([]).")
    lineas.append("cargar_sintomas([H|T]) :-")
    lineas.append("    assertz(tiene_sintoma(H)),")
    lineas.append("    cargar_sintomas(T).")
    lineas.append("")
    lineas.append("eliminar_duplicados(Lista, SinDuplicados) :-")
    lineas.append("    eliminar_duplicados(Lista, [], SinDuplicados).")
    lineas.append("")
    lineas.append("eliminar_duplicados([], Acum, Acum).")
    lineas.append("eliminar_duplicados([diagnostico(Falla, _, _)|Resto], Acum, Resultado) :-")
    lineas.append("    member(diagnostico(Falla, _, _), Acum),")
    lineas.append("    !,")
    lineas.append("    eliminar_duplicados(Resto, Acum, Resultado).")
    lineas.append("eliminar_duplicados([H|Resto], Acum, Resultado) :-")
    lineas.append("    eliminar_duplicados(Resto, [H|Acum], Resultado).")
    lineas.append("")
    lineas.append("obtener_todos_los_sintomas(Lista) :-")
    lineas.append("    findall(sintoma(Id, Desc),")
    lineas.append("        (sintoma(Id), descripcion_sintoma(Id, Desc)),")
    lineas.append("        Lista).")
    lineas.append("")
    lineas.append("obtener_diagnostico(SintomasUsuario, Resultados) :-")
    lineas.append("    retractall(tiene_sintoma(_)),")
    lineas.append("    cargar_sintomas(SintomasUsuario),")
    lineas.append("    findall(diagnostico(Falla, Desc, Recs),")
    lineas.append("        (diagnosticar(Falla),")
    lineas.append("         descripcion_falla(Falla, Desc),")
    lineas.append("         recomendaciones(Falla, Recs)),")
    lineas.append("        ResultadosDuplicados),")
    lineas.append("    eliminar_duplicados(ResultadosDuplicados, Resultados).")
    lineas.append("")

    # --- SALIDA JSON ---
    lineas.append(":- use_module(library(http/json)).")
    lineas.append("")
    lineas.append("cmd_sintomas :-")
    lineas.append("    findall(json([id=Id, descripcion=Desc]),")
    lineas.append("        (sintoma(Id), descripcion_sintoma(Id, Desc)),")
    lineas.append("        Lista),")
    lineas.append("    json_write(current_output, Lista, [width(0)]), nl.")
    lineas.append("")
    lineas.append("cmd_diagnostico(SintomasAtom) :-")
    lineas.append("    term_to_atom(Sintomas, SintomasAtom),")
    lineas.append("    retractall(tiene_sintoma(_)),")
    lineas.append("    cargar_sintomas(Sintomas),")
    lineas.append("    findall(Falla-json([falla=Falla, descripcion=Desc, recomendaciones=Recs]),")
    lineas.append("        (diagnosticar(Falla),")
    lineas.append("         descripcion_falla(Falla, Desc),")
    lineas.append("         recomendaciones(Falla, Recs)),")
    lineas.append("        Pares),")
    lineas.append("    quitar_pares_duplicados(Pares, [], ParesSinDup),")
    lineas.append("    pairs_values(ParesSinDup, Resultado),")
    lineas.append("    json_write(current_output, Resultado, [width(0)]), nl.")
    lineas.append("")
    lineas.append("quitar_pares_duplicados([], Acum, Acum).")
    lineas.append("quitar_pares_duplicados([K-_|Resto], Acum, Resultado) :-")
    lineas.append("    member(K-_, Acum), !,")
    lineas.append("    quitar_pares_duplicados(Resto, Acum, Resultado).")
    lineas.append("quitar_pares_duplicados([Par|Resto], Acum, Resultado) :-")
    lineas.append("    quitar_pares_duplicados(Resto, [Par|Acum], Resultado).")

    contenido = "\n".join(lineas) + "\n"

    with open(PROLOG_FILE, "w", encoding="utf-8") as f:
        f.write(contenido)
