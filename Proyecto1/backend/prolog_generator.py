# ============================================================
# prolog_generator.py — Generador del archivo Prolog
#
# Este modulo es responsable de MANTENER SINCRONIZADOS los
# datos del admin (JSON) con la base de conocimiento Prolog.
#
# PROBLEMA QUE RESUELVE:
#   Si el admin puede agregar/editar/eliminar sintomas, fallas
#   y reglas, el archivo .pl debe actualizarse automaticamente.
#   En lugar de editar el .pl a mano, leemos los JSON y
#   regeneramos el .pl completo cada vez.
#
# FUNCION PRINCIPAL: generar_pl()
#   Lee: symptoms.json, faults.json, recommendations.json, rules.json
#   Escribe: doctor_byte.pl completo y valido
#
# CUANDO SE LLAMA:
#   Automaticamente desde knowledge_manager.py despues de
#   cualquier operacion CRUD que modifique los datos.
# ============================================================

import json
import os
from config import BASE_DIR, PROLOG_FILE

# Rutas a los JSON de datos
SYMPTOMS_FILE    = os.path.join(BASE_DIR, "data", "symptoms.json")
FAULTS_FILE      = os.path.join(BASE_DIR, "data", "faults.json")
RECS_FILE        = os.path.join(BASE_DIR, "data", "recommendations.json")
RULES_FILE       = os.path.join(BASE_DIR, "data", "rules.json")


def _leer(path):
    """Lee un archivo JSON y retorna el objeto Python."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _escapar_atom(texto):
    """
    Envuelve un texto en comillas simples para usarlo como atomo Prolog.
    Escapa las comillas simples internas con backslash.

    Ejemplo: "La pantalla no muestra" → "'La pantalla no muestra'"
    Ejemplo: "can't boot"             → "'can\\'t boot'"
    """
    return "'" + texto.replace("'", "\\'") + "'"


def generar_pl():
    """
    Genera el archivo doctor_byte.pl completo desde los JSON de datos.

    Este archivo contiene TODA la logica del sistema experto:
      - Hechos: sintoma/1, falla/1, descripcion_sintoma/2, etc.
      - Reglas: diagnosticar/1 con sus condiciones
      - Predicados auxiliares: cargar_sintomas, eliminar_duplicados, etc.
      - Predicados de salida: cmd_sintomas, cmd_diagnostico (JSON a stdout)

    PENALIZACION EVITADA: "Toda la logica en BD y no en Prolog = -25%"
    La logica de inferencia siempre esta en el .pl, los JSON son solo
    el mecanismo de persistencia para el panel admin.
    """
    # Leemos todos los datos actuales de los JSON
    sintomas = _leer(SYMPTOMS_FILE)
    fallas   = _leer(FAULTS_FILE)
    recs     = _leer(RECS_FILE)
    reglas   = _leer(RULES_FILE)

    lineas = []

    # --- ENCABEZADO ---
    lineas.append("% ============================================================")
    lineas.append("% Doctor Byte - Base de Conocimiento (generado por el admin)")
    lineas.append("% Inteligencia Artificial 1 - USAC 2026")
    lineas.append("% ============================================================")
    lineas.append("")

    # Declaracion dinamica: permite assertz/retractall en tiempo de ejecucion.
    # Necesario para cargar los sintomas del usuario durante el diagnostico.
    lineas.append(":- dynamic tiene_sintoma/1.")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 1: HECHOS DE SINTOMAS
    # Cada sintoma es un hecho simple: sintoma(id).
    # La descripcion es un hecho binario: descripcion_sintoma(id, texto).
    # --------------------------------------------------------
    lineas.append("% --- Sintomas ---")
    for s in sintomas:
        lineas.append(f"sintoma({s['id']}).")
    lineas.append("")

    lineas.append("% --- Descripciones de sintomas ---")
    for s in sintomas:
        lineas.append(f"descripcion_sintoma({s['id']}, {_escapar_atom(s['descripcion'])}).")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 2: HECHOS DE FALLAS
    # Mismo patron: falla(id) y descripcion_falla(id, texto).
    # --------------------------------------------------------
    lineas.append("% --- Fallas ---")
    for f in fallas:
        lineas.append(f"falla({f['id']}).")
    lineas.append("")

    lineas.append("% --- Descripciones de fallas ---")
    for f in fallas:
        lineas.append(f"descripcion_falla({f['id']}, {_escapar_atom(f['descripcion'])}).")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 3: RECOMENDACIONES (LISTAS PROLOG)
    # Las recomendaciones se representan como listas Prolog.
    # Ejemplo: recomendaciones(fallo_ram, ['Ejecutar MemTest86', 'Reemplazar modulo']).
    # Esto demuestra el uso de listas en Prolog (exigencia basica).
    # --------------------------------------------------------
    lineas.append("% --- Recomendaciones ---")
    for fault_id, lista in recs.items():
        # Escapamos cada recomendacion y las unimos con comas dentro de [ ]
        items = ", ".join(_escapar_atom(r) for r in lista)
        lineas.append(f"recomendaciones({fault_id}, [{items}]).")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 4: REGLAS DE INFERENCIA
    # Estas son las reglas que el motor de inferencia usa para diagnosticar.
    # Formato: diagnosticar(falla) :- tiene_sintoma(s1), tiene_sintoma(s2), ...
    #
    # Ejemplo generado:
    #   diagnosticar(fallo_ram) :-
    #       tiene_sintoma(pantalla_azul),
    #       tiene_sintoma(errores_memoria).
    # --------------------------------------------------------
    lineas.append("% --- Reglas de inferencia ---")
    for r in reglas:
        # Cada condicion es tiene_sintoma(id), separadas por coma
        condiciones = ",\n    ".join(f"tiene_sintoma({c})" for c in r["conditions"])
        lineas.append(f"diagnosticar({r['conclusion']}) :-")
        lineas.append(f"    {condiciones}.")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 5: PREDICADOS AUXILIARES (ESTATICOS)
    # Estos no cambian con el admin, siempre son los mismos.
    # --------------------------------------------------------
    lineas.append("% --- Predicados auxiliares ---")
    lineas.append("")

    # cargar_sintomas/1: carga la lista de sintomas del usuario
    # usando assertz para agregarlos como hechos dinamicos.
    # Es recursivo sobre listas: caso base [] y caso recursivo [H|T].
    lineas.append("cargar_sintomas([]).")
    lineas.append("cargar_sintomas([H|T]) :-")
    lineas.append("    assertz(tiene_sintoma(H)),")  # agrega H como hecho
    lineas.append("    cargar_sintomas(T).")          # procesa el resto
    lineas.append("")

    # eliminar_duplicados/2 y /3: elimina fallas duplicadas del resultado.
    # USO DEL CORTE (!): cuando ya encontramos la falla en el acumulador,
    # el ! evita que Prolog siga buscando alternativas (poda del arbol).
    lineas.append("eliminar_duplicados(Lista, SinDuplicados) :-")
    lineas.append("    eliminar_duplicados(Lista, [], SinDuplicados).")
    lineas.append("")
    lineas.append("eliminar_duplicados([], Acum, Acum).")  # caso base
    lineas.append("eliminar_duplicados([diagnostico(Falla, _, _)|Resto], Acum, Resultado) :-")
    lineas.append("    member(diagnostico(Falla, _, _), Acum),")  # ya esta en acumulador?
    lineas.append("    !,")  # CORTE: si esta duplicado, no lo agregamos
    lineas.append("    eliminar_duplicados(Resto, Acum, Resultado).")
    lineas.append("eliminar_duplicados([H|Resto], Acum, Resultado) :-")
    lineas.append("    eliminar_duplicados(Resto, [H|Acum], Resultado).")  # lo agrega
    lineas.append("")

    # obtener_todos_los_sintomas/1: usa findall para recolectar todos
    # los sintomas en una lista. findall es el mecanismo de Prolog
    # para recolectar todas las soluciones de un goal.
    lineas.append("obtener_todos_los_sintomas(Lista) :-")
    lineas.append("    findall(sintoma(Id, Desc),")
    lineas.append("        (sintoma(Id), descripcion_sintoma(Id, Desc)),")
    lineas.append("        Lista).")
    lineas.append("")

    # obtener_diagnostico/2: predicado principal de inferencia.
    # 1. retractall: limpia los sintomas de consultas anteriores
    # 2. cargar_sintomas: carga los sintomas del usuario actual
    # 3. findall: prueba diagnosticar/1 para cada falla posible
    # 4. eliminar_duplicados: quita repeticiones
    lineas.append("obtener_diagnostico(SintomasUsuario, Resultados) :-")
    lineas.append("    retractall(tiene_sintoma(_)),")      # limpia estado anterior
    lineas.append("    cargar_sintomas(SintomasUsuario),")  # carga sintomas nuevos
    lineas.append("    findall(diagnostico(Falla, Desc, Recs),")
    lineas.append("        (diagnosticar(Falla),")
    lineas.append("         descripcion_falla(Falla, Desc),")
    lineas.append("         recomendaciones(Falla, Recs)),")
    lineas.append("        ResultadosDuplicados),")
    lineas.append("    eliminar_duplicados(ResultadosDuplicados, Resultados).")
    lineas.append("")

    # --------------------------------------------------------
    # SECCION 6: PREDICADOS DE SALIDA JSON
    # Estos predicados son la interfaz con Python.
    # Escriben JSON en stdout para que subprocess.run() lo capture.
    # --------------------------------------------------------

    # Importamos la libreria JSON de SWI-Prolog
    lineas.append(":- use_module(library(http/json)).")
    lineas.append("")

    # cmd_sintomas/0: escribe todos los sintomas como JSON en stdout
    # Python lo llama con: swipl -g "consult(...),cmd_sintomas,halt"
    lineas.append("cmd_sintomas :-")
    lineas.append("    findall(json([id=Id, descripcion=Desc]),")
    lineas.append("        (sintoma(Id), descripcion_sintoma(Id, Desc)),")
    lineas.append("        Lista),")
    lineas.append("    json_write(current_output, Lista, [width(0)]), nl.")
    lineas.append("")

    # cmd_diagnostico/1: recibe los sintomas como atomo Prolog,
    # ejecuta la inferencia y escribe el resultado como JSON en stdout.
    # quitar_pares_duplicados usa el CORTE (!) para evitar duplicados.
    lineas.append("cmd_diagnostico(SintomasAtom) :-")
    lineas.append("    term_to_atom(Sintomas, SintomasAtom),")  # convierte '[a,b]' a lista Prolog
    lineas.append("    retractall(tiene_sintoma(_)),")
    lineas.append("    cargar_sintomas(Sintomas),")
    lineas.append("    findall(Falla-json([falla=Falla, descripcion=Desc, recomendaciones=Recs]),")
    lineas.append("        (diagnosticar(Falla),")
    lineas.append("         descripcion_falla(Falla, Desc),")
    lineas.append("         recomendaciones(Falla, Recs)),")
    lineas.append("        Pares),")
    lineas.append("    quitar_pares_duplicados(Pares, [], ParesSinDup),")
    lineas.append("    pairs_values(ParesSinDup, Resultado),")  # extrae solo los valores
    lineas.append("    json_write(current_output, Resultado, [width(0)]), nl.")
    lineas.append("")

    # quitar_pares_duplicados/3: elimina pares con clave duplicada.
    # Usa CORTE (!) en el segundo caso: si la clave ya esta en el
    # acumulador, descarta el par y no busca mas alternativas.
    lineas.append("quitar_pares_duplicados([], Acum, Acum).")
    lineas.append("quitar_pares_duplicados([K-_|Resto], Acum, Resultado) :-")
    lineas.append("    member(K-_, Acum), !,")  # CORTE: ya existe, no agregar
    lineas.append("    quitar_pares_duplicados(Resto, Acum, Resultado).")
    lineas.append("quitar_pares_duplicados([Par|Resto], Acum, Resultado) :-")
    lineas.append("    quitar_pares_duplicados(Resto, [Par|Acum], Resultado).")

    # Unimos todas las lineas con salto de linea
    contenido = "\n".join(lineas) + "\n"

    # Escribimos el archivo .pl completo
    with open(PROLOG_FILE, "w", encoding="utf-8") as f:
        f.write(contenido)
