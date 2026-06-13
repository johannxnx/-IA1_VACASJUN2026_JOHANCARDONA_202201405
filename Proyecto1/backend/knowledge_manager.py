import json
import os
import uuid
from prolog_generator import generar_pl

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SYMPTOMS_FILE = os.path.join(BASE_DIR, "data", "symptoms.json")
FAULTS_FILE   = os.path.join(BASE_DIR, "data", "faults.json")
RECS_FILE     = os.path.join(BASE_DIR, "data", "recommendations.json")
RULES_FILE    = os.path.join(BASE_DIR, "data", "rules.json")
BOT_CFG_FILE  = os.path.join(BASE_DIR, "data", "bot_config.json")


def _leer(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _escribir(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
# SINTOMAS
# ============================================================

def get_sintomas():
    return _leer(SYMPTOMS_FILE)

def add_sintoma(id_, descripcion):
    data = _leer(SYMPTOMS_FILE)
    if any(s["id"] == id_ for s in data):
        raise ValueError(f"Ya existe un sintoma con id '{id_}'")
    data.append({"id": id_, "descripcion": descripcion})
    _escribir(SYMPTOMS_FILE, data)
    generar_pl()

def update_sintoma(id_, descripcion):
    data = _leer(SYMPTOMS_FILE)
    for s in data:
        if s["id"] == id_:
            s["descripcion"] = descripcion
            _escribir(SYMPTOMS_FILE, data)
            generar_pl()
            return
    raise ValueError(f"Sintoma '{id_}' no encontrado")

def delete_sintoma(id_):
    data = _leer(SYMPTOMS_FILE)
    nueva = [s for s in data if s["id"] != id_]
    if len(nueva) == len(data):
        raise ValueError(f"Sintoma '{id_}' no encontrado")
    _escribir(SYMPTOMS_FILE, nueva)
    # Eliminar reglas que usen este sintoma
    reglas = _leer(RULES_FILE)
    _escribir(RULES_FILE, [r for r in reglas if id_ not in r["conditions"]])
    generar_pl()

# ============================================================
# FALLAS
# ============================================================

def get_fallas():
    return _leer(FAULTS_FILE)

def add_falla(id_, descripcion):
    data = _leer(FAULTS_FILE)
    if any(f["id"] == id_ for f in data):
        raise ValueError(f"Ya existe una falla con id '{id_}'")
    data.append({"id": id_, "descripcion": descripcion})
    _escribir(FAULTS_FILE, data)
    recs = _leer(RECS_FILE)
    recs[id_] = []
    _escribir(RECS_FILE, recs)
    generar_pl()

def update_falla(id_, descripcion):
    data = _leer(FAULTS_FILE)
    for f in data:
        if f["id"] == id_:
            f["descripcion"] = descripcion
            _escribir(FAULTS_FILE, data)
            generar_pl()
            return
    raise ValueError(f"Falla '{id_}' no encontrada")

def delete_falla(id_):
    data = _leer(FAULTS_FILE)
    nueva = [f for f in data if f["id"] != id_]
    if len(nueva) == len(data):
        raise ValueError(f"Falla '{id_}' no encontrada")
    _escribir(FAULTS_FILE, nueva)
    recs = _leer(RECS_FILE)
    recs.pop(id_, None)
    _escribir(RECS_FILE, recs)
    reglas = _leer(RULES_FILE)
    _escribir(RULES_FILE, [r for r in reglas if r["conclusion"] != id_])
    generar_pl()

# ============================================================
# RECOMENDACIONES
# ============================================================

def get_recomendaciones():
    return _leer(RECS_FILE)

def update_recomendaciones(fault_id, lista):
    recs = _leer(RECS_FILE)
    recs[fault_id] = lista
    _escribir(RECS_FILE, recs)
    generar_pl()

# ============================================================
# REGLAS
# ============================================================

def get_reglas():
    return _leer(RULES_FILE)

def add_regla(conclusion, conditions):
    reglas = _leer(RULES_FILE)
    nueva = {"id": f"r{uuid.uuid4().hex[:6]}", "conclusion": conclusion, "conditions": conditions}
    reglas.append(nueva)
    _escribir(RULES_FILE, reglas)
    generar_pl()
    return nueva

def update_regla(rule_id, conclusion, conditions):
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
    reglas = _leer(RULES_FILE)
    nueva = [r for r in reglas if r["id"] != rule_id]
    if len(nueva) == len(reglas):
        raise ValueError(f"Regla '{rule_id}' no encontrada")
    _escribir(RULES_FILE, nueva)
    generar_pl()

# ============================================================
# CONFIGURACION DEL BOT
# ============================================================

def get_bot_config():
    return _leer(BOT_CFG_FILE)

def update_bot_config(datos):
    cfg = _leer(BOT_CFG_FILE)
    cfg.update(datos)
    _escribir(BOT_CFG_FILE, cfg)
    return cfg
