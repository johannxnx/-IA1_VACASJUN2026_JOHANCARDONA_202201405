# ============================================================
# knowledge_manager.py — Gestion de la base de conocimiento
#
# Este modulo implementa el CRUD (Create, Read, Update, Delete)
# para todas las entidades del sistema:
#   - Sintomas
#   - Fallas diagnosticables
#   - Recomendaciones por falla
#   - Reglas de inferencia
#   - Configuracion del bot de Telegram
#
# ARQUITECTURA DE PERSISTENCIA:
#   Los datos se guardan en archivos JSON (sin base de datos).
#   Cada vez que el admin modifica algo, este modulo:
#     1. Lee el JSON correspondiente
#     2. Aplica el cambio
#     3. Escribe el JSON actualizado
#     4. Llama a prolog_generator.generar_pl() para regenerar
#        el archivo doctor_byte.pl con los nuevos datos
#
# Esto garantiza que la logica de inferencia siempre este
# actualizada en Prolog y no en la "base de datos" JSON.
# ============================================================

import json
import os
import uuid
from prolog_generator import generar_pl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas a los archivos JSON de persistencia
SYMPTOMS_FILE = os.path.join(BASE_DIR, "data", "symptoms.json")
FAULTS_FILE   = os.path.join(BASE_DIR, "data", "faults.json")
RECS_FILE     = os.path.join(BASE_DIR, "data", "recommendations.json")
RULES_FILE    = os.path.join(BASE_DIR, "data", "rules.json")
BOT_CFG_FILE  = os.path.join(BASE_DIR, "data", "bot_config.json")


# --- Funciones auxiliares de I/O ---

def _leer(path):
    """Lee y parsea un archivo JSON. Retorna el objeto Python correspondiente."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _escribir(path, data):
    """Serializa un objeto Python y lo escribe en el archivo JSON."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# SINTOMAS
# Un sintoma tiene: { "id": "pantalla_negra", "descripcion": "..." }
# ============================================================

def get_sintomas():
    """Retorna la lista completa de sintomas desde symptoms.json."""
    return _leer(SYMPTOMS_FILE)

def add_sintoma(id_, descripcion):
    """
    Agrega un nuevo sintoma a la base de conocimiento.
    Lanza ValueError si ya existe un sintoma con ese ID.
    Despues de guardar, regenera el archivo Prolog.
    """
    data = _leer(SYMPTOMS_FILE)
    if any(s["id"] == id_ for s in data):
        raise ValueError(f"Ya existe un sintoma con id '{id_}'")
    data.append({"id": id_, "descripcion": descripcion})
    _escribir(SYMPTOMS_FILE, data)
    generar_pl()  # Regenera doctor_byte.pl con el nuevo sintoma incluido

def update_sintoma(id_, descripcion):
    """Actualiza la descripcion de un sintoma existente."""
    data = _leer(SYMPTOMS_FILE)
    for s in data:
        if s["id"] == id_:
            s["descripcion"] = descripcion
            _escribir(SYMPTOMS_FILE, data)
            generar_pl()
            return
    raise ValueError(f"Sintoma '{id_}' no encontrado")

def delete_sintoma(id_):
    """
    Elimina un sintoma y todas las reglas que lo referencian.
    Esto mantiene la consistencia de la base de conocimiento:
    no pueden existir reglas que usen un sintoma inexistente.
    """
    data = _leer(SYMPTOMS_FILE)
    nueva = [s for s in data if s["id"] != id_]
    if len(nueva) == len(data):
        raise ValueError(f"Sintoma '{id_}' no encontrado")
    _escribir(SYMPTOMS_FILE, nueva)

    # Eliminamos en cascada las reglas que usen este sintoma en sus condiciones
    reglas = _leer(RULES_FILE)
    _escribir(RULES_FILE, [r for r in reglas if id_ not in r["conditions"]])

    generar_pl()


# ============================================================
# FALLAS
# Una falla tiene: { "id": "fallo_ram", "descripcion": "..." }
# ============================================================

def get_fallas():
    """Retorna la lista completa de fallas desde faults.json."""
    return _leer(FAULTS_FILE)

def add_falla(id_, descripcion):
    """
    Agrega una nueva falla diagnosticable.
    Ademas crea una entrada vacia en recommendations.json
    para que la falla pueda recibir recomendaciones.
    """
    data = _leer(FAULTS_FILE)
    if any(f["id"] == id_ for f in data):
        raise ValueError(f"Ya existe una falla con id '{id_}'")
    data.append({"id": id_, "descripcion": descripcion})
    _escribir(FAULTS_FILE, data)
    # Inicializa la lista de recomendaciones vacia para esta falla
    recs = _leer(RECS_FILE)
    recs[id_] = []
    _escribir(RECS_FILE, recs)
    generar_pl()

def update_falla(id_, descripcion):
    """Actualiza la descripcion de una falla existente."""
    data = _leer(FAULTS_FILE)
    for f in data:
        if f["id"] == id_:
            f["descripcion"] = descripcion
            _escribir(FAULTS_FILE, data)
            generar_pl()
            return
    raise ValueError(f"Falla '{id_}' no encontrada")

def delete_falla(id_):
    """
    Elimina una falla y en cascada:
      - Sus recomendaciones en recommendations.json
      - Todas las reglas que tengan esa falla como conclusion
    """
    data = _leer(FAULTS_FILE)
    nueva = [f for f in data if f["id"] != id_]
    if len(nueva) == len(data):
        raise ValueError(f"Falla '{id_}' no encontrada")
    _escribir(FAULTS_FILE, nueva)

    # Elimina las recomendaciones de esta falla
    recs = _leer(RECS_FILE)
    recs.pop(id_, None)
    _escribir(RECS_FILE, recs)

    # Elimina las reglas cuya conclusion es esta falla
    reglas = _leer(RULES_FILE)
    _escribir(RULES_FILE, [r for r in reglas if r["conclusion"] != id_])

    generar_pl()


# ============================================================
# RECOMENDACIONES
# Son listas de strings por falla: { "fallo_ram": ["rec1", "rec2"] }
# En Prolog se representan como: recomendaciones(fallo_ram, ['rec1','rec2']).
# ============================================================

def get_recomendaciones():
    """Retorna el diccionario completo de recomendaciones por falla."""
    return _leer(RECS_FILE)

def update_recomendaciones(fault_id, lista):
    """
    Reemplaza la lista completa de recomendaciones para una falla.
    El frontend envia la lista completa modificada.
    """
    recs = _leer(RECS_FILE)
    recs[fault_id] = lista
    _escribir(RECS_FILE, recs)
    generar_pl()


# ============================================================
# REGLAS DE INFERENCIA
# Una regla tiene: { "id": "r1a2b3", "conclusion": "fallo_ram", "conditions": ["pantalla_azul"] }
# En Prolog se genera como:
#   diagnosticar(fallo_ram) :- tiene_sintoma(pantalla_azul).
# ============================================================

def get_reglas():
    """Retorna la lista de todas las reglas de inferencia."""
    return _leer(RULES_FILE)

def add_regla(conclusion, conditions):
    """
    Crea una nueva regla de inferencia.
    Genera un ID unico de 6 caracteres hexadecimales.
    """
    reglas = _leer(RULES_FILE)
    # uuid4().hex[:6] genera un ID unico como "r4a7b2"
    nueva = {
        "id":         f"r{uuid.uuid4().hex[:6]}",
        "conclusion": conclusion,   # la falla que se diagnostica
        "conditions": conditions    # lista de sintomas que deben estar presentes
    }
    reglas.append(nueva)
    _escribir(RULES_FILE, reglas)
    generar_pl()
    return nueva

def update_regla(rule_id, conclusion, conditions):
    """Actualiza la conclusion y/o condiciones de una regla existente."""
    reglas = _leer(RULES_FILE)
    for r in reglas:
        if r["id"] == rule_id:
            r["conclusion"] = conclusion
            r["conditions"] = conditions
            _escribir(RULES_FILE, reglas)
            generar_pl()
            return r
    raise ValueError(f"Regla '{rule_id}' no encontrada")

def delete_regla(rule_id):
    """Elimina una regla de inferencia por su ID."""
    reglas = _leer(RULES_FILE)
    nueva = [r for r in reglas if r["id"] != rule_id]
    if len(nueva) == len(reglas):
        raise ValueError(f"Regla '{rule_id}' no encontrada")
    _escribir(RULES_FILE, nueva)
    generar_pl()


# ============================================================
# CONFIGURACION DEL BOT DE TELEGRAM
# Persistida en bot_config.json con los campos:
#   - enabled: bool (activar/desactivar notificaciones)
#   - chat_id: string (a donde enviar, editable desde el admin)
#   - mensaje_encabezado: titulo del mensaje
#   - mensaje_sin_diagnostico: texto cuando Prolog no encuentra nada
# ============================================================

def get_bot_config():
    """Retorna la configuracion actual del bot de Telegram."""
    return _leer(BOT_CFG_FILE)

def update_bot_config(datos):
    """
    Actualiza la configuracion del bot de forma parcial.
    Solo se modifican los campos que vengan en 'datos'.
    """
    cfg = _leer(BOT_CFG_FILE)
    cfg.update(datos)  # merge: solo sobreescribe los campos enviados
    _escribir(BOT_CFG_FILE, cfg)
    return cfg
