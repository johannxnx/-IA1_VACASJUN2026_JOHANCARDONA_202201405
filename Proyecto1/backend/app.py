# ============================================================
# app.py — Servidor principal Flask (API REST)
#
# Este archivo define todos los endpoints del sistema.
# Es el punto de entrada del backend y actua como intermediario
# entre el frontend (HTML/JS) y los modulos de logica.
#
# PATRON DE ARQUITECTURA: Capas separadas
#   Frontend (HTML/JS)
#       ↓ HTTP (JSON)
#   app.py  ← aqui estamos
#       ↓ llama a modulos especializados
#   prolog_interface.py → SWI-Prolog (inferencia)
#   knowledge_manager.py → JSON (persistencia)
#   history_manager.py   → JSON (historial)
#   telegram_service.py  → API Telegram (notificaciones)
#
# Endpoints disponibles:
#   GET  /api/sintomas          — lista de sintomas para el formulario
#   POST /api/diagnostico       — ejecuta el diagnostico en Prolog
#   GET  /api/historial         — historial de diagnosticos
#   GET  /api/historial/<id>    — diagnostico especifico
#   (+ 14 endpoints de admin para CRUD de la base de conocimiento)
# ============================================================

import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import prolog_interface
import history_manager
import telegram_service
import knowledge_manager as km
from config import FLASK_PORT, FLASK_DEBUG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Creamos la app Flask indicando donde estan las plantillas y archivos estaticos.
# El frontend esta en ../frontend/ separado del backend.
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "frontend", "static")
)

# CORS permite que el navegador haga peticiones al backend desde otro origen.
# En desarrollo el frontend corre en el mismo puerto, pero es buena practica.
CORS(app)


# ============================================================
# ENDPOINT PRINCIPAL: GET /
# Sirve el archivo index.html (la interfaz del usuario)
# ============================================================
@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# ENDPOINT: GET /api/sintomas
#
# El frontend llama esto al cargar la pagina para construir
# el grid de tarjetas de sintomas dinamicamente.
#
# Respuesta exitosa:
#   { "ok": true, "sintomas": [{"id": "...", "descripcion": "..."}, ...] }
#
# Error:
#   { "ok": false, "error": "mensaje" }, HTTP 500
# ============================================================
@app.route("/api/sintomas", methods=["GET"])
def get_sintomas():
    try:
        # Llama a prolog_interface que ejecuta swipl y parsea el JSON de salida
        sintomas = prolog_interface.obtener_sintomas()
        return jsonify({"ok": True, "sintomas": sintomas})
    except Exception as e:
        # Manejo de errores: cualquier excepcion retorna 500 con descripcion
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ENDPOINT: POST /api/diagnostico
#
# Recibe los sintomas del usuario, los pasa a Prolog,
# guarda el resultado en historial y notifica por Telegram.
#
# Body JSON esperado:
#   { "sintomas": ["pantalla_negra", "ruido_disco"] }
#
# Validaciones:
#   - El body debe ser JSON valido
#   - Debe existir el campo "sintomas"
#   - "sintomas" debe ser una lista no vacia
# ============================================================
@app.route("/api/diagnostico", methods=["POST"])
def post_diagnostico():
    # silent=True evita que Flask lance excepcion si el body no es JSON valido
    datos = request.get_json(silent=True)

    # Validacion de entrada: campo obligatorio
    if not datos or "sintomas" not in datos:
        return jsonify({"ok": False, "error": "Se requiere el campo 'sintomas'"}), 400

    sintomas = datos["sintomas"]

    # Validacion: debe ser una lista con al menos un elemento
    if not isinstance(sintomas, list) or len(sintomas) == 0:
        return jsonify({"ok": False, "error": "'sintomas' debe ser una lista no vacia"}), 400

    try:
        # 1. INFERENCIA: Prolog analiza los sintomas y retorna los diagnosticos
        diagnosticos = prolog_interface.obtener_diagnostico(sintomas)

        # 2. PERSISTENCIA: Guardamos el resultado en history.json
        #    Independientemente de si hay diagnosticos o no
        entrada = history_manager.guardar_diagnostico(sintomas, diagnosticos)

        # 3. NOTIFICACION: Enviamos a Telegram de forma no bloqueante.
        #    Si falla (sin internet, bot desactivado, etc.), NO afecta la respuesta al usuario.
        telegram_service.enviar_notificacion(sintomas, diagnosticos)

        return jsonify({
            "ok": True,
            "id":          entrada["id"],        # UUID unico de esta consulta
            "timestamp":   entrada["timestamp"],  # Fecha/hora en formato ISO
            "sintomas":    sintomas,
            "diagnosticos": diagnosticos
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ENDPOINT: GET /api/historial
#
# Retorna todos los diagnosticos guardados, del mas reciente
# al mas antiguo (lista invertida).
# ============================================================
@app.route("/api/historial", methods=["GET"])
def get_historial():
    try:
        historial = history_manager.obtener_historial()
        return jsonify({"ok": True, "historial": historial})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ENDPOINT: GET /api/historial/<id>
#
# Retorna un diagnostico especifico buscado por su UUID.
# Retorna 404 si el ID no existe.
# ============================================================
@app.route("/api/historial/<entrada_id>", methods=["GET"])
def get_entrada_historial(entrada_id):
    try:
        entrada = history_manager.obtener_entrada(entrada_id)
        if entrada is None:
            return jsonify({"ok": False, "error": "Entrada no encontrada"}), 404
        return jsonify({"ok": True, "entrada": entrada})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - SINTOMAS
# CRUD completo para gestionar sintomas desde el panel admin.
# Cada modificacion regenera automaticamente el archivo .pl
# a traves de knowledge_manager → prolog_generator.
# ============================================================

@app.route("/api/admin/sintomas", methods=["GET"])
def admin_get_sintomas():
    try:
        return jsonify({"ok": True, "sintomas": km.get_sintomas()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/sintomas", methods=["POST"])
def admin_add_sintoma():
    # Requiere: { "id": "nuevo_sintoma", "descripcion": "Texto legible" }
    d = request.get_json(silent=True) or {}
    if not d.get("id") or not d.get("descripcion"):
        return jsonify({"ok": False, "error": "Se requieren 'id' y 'descripcion'"}), 400
    try:
        km.add_sintoma(d["id"].strip(), d["descripcion"].strip())
        return jsonify({"ok": True})
    except ValueError as e:
        # ValueError indica ID duplicado → HTTP 409 Conflict
        return jsonify({"ok": False, "error": str(e)}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/sintomas/<sid>", methods=["PUT"])
def admin_update_sintoma(sid):
    # El ID no cambia, solo la descripcion
    d = request.get_json(silent=True) or {}
    if not d.get("descripcion"):
        return jsonify({"ok": False, "error": "Se requiere 'descripcion'"}), 400
    try:
        km.update_sintoma(sid, d["descripcion"].strip())
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/sintomas/<sid>", methods=["DELETE"])
def admin_delete_sintoma(sid):
    # Al eliminar un sintoma tambien se eliminan las reglas que lo usan
    try:
        km.delete_sintoma(sid)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - FALLAS
# CRUD para las fallas diagnosticables.
# Al eliminar una falla se eliminan sus recomendaciones y reglas.
# ============================================================

@app.route("/api/admin/fallas", methods=["GET"])
def admin_get_fallas():
    try:
        return jsonify({"ok": True, "fallas": km.get_fallas()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/fallas", methods=["POST"])
def admin_add_falla():
    d = request.get_json(silent=True) or {}
    if not d.get("id") or not d.get("descripcion"):
        return jsonify({"ok": False, "error": "Se requieren 'id' y 'descripcion'"}), 400
    try:
        km.add_falla(d["id"].strip(), d["descripcion"].strip())
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/fallas/<fid>", methods=["PUT"])
def admin_update_falla(fid):
    d = request.get_json(silent=True) or {}
    if not d.get("descripcion"):
        return jsonify({"ok": False, "error": "Se requiere 'descripcion'"}), 400
    try:
        km.update_falla(fid, d["descripcion"].strip())
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/fallas/<fid>", methods=["DELETE"])
def admin_delete_falla(fid):
    try:
        km.delete_falla(fid)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - RECOMENDACIONES
# Las recomendaciones se gestionan por falla.
# Se reemplaza toda la lista de una falla en cada PUT.
# ============================================================

@app.route("/api/admin/recomendaciones", methods=["GET"])
def admin_get_recs():
    try:
        return jsonify({"ok": True, "recomendaciones": km.get_recomendaciones()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/recomendaciones/<fault_id>", methods=["PUT"])
def admin_update_recs(fault_id):
    # Requiere: { "lista": ["rec1", "rec2", ...] }
    d = request.get_json(silent=True) or {}
    if "lista" not in d or not isinstance(d["lista"], list):
        return jsonify({"ok": False, "error": "Se requiere 'lista' (array)"}), 400
    try:
        km.update_recomendaciones(fault_id, d["lista"])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - REGLAS DE INFERENCIA
# CRUD para las reglas que conectan sintomas con fallas.
# Cada regla tiene: id, conclusion (falla), conditions (sintomas).
# ============================================================

@app.route("/api/admin/reglas", methods=["GET"])
def admin_get_reglas():
    try:
        return jsonify({"ok": True, "reglas": km.get_reglas()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/reglas", methods=["POST"])
def admin_add_regla():
    # Requiere: { "conclusion": "fallo_ram", "conditions": ["pantalla_azul", "errores_memoria"] }
    d = request.get_json(silent=True) or {}
    if not d.get("conclusion") or not d.get("conditions"):
        return jsonify({"ok": False, "error": "Se requieren 'conclusion' y 'conditions'"}), 400
    try:
        nueva = km.add_regla(d["conclusion"], d["conditions"])
        return jsonify({"ok": True, "regla": nueva})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/reglas/<rid>", methods=["PUT"])
def admin_update_regla(rid):
    d = request.get_json(silent=True) or {}
    if not d.get("conclusion") or not d.get("conditions"):
        return jsonify({"ok": False, "error": "Se requieren 'conclusion' y 'conditions'"}), 400
    try:
        km.update_regla(rid, d["conclusion"], d["conditions"])
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/reglas/<rid>", methods=["DELETE"])
def admin_delete_regla(rid):
    try:
        km.delete_regla(rid)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - CONFIGURACION DEL BOT DE TELEGRAM
# Permite activar/desactivar el bot, cambiar mensajes
# y modificar el chat_id desde la interfaz web.
# ============================================================

@app.route("/api/admin/bot-config", methods=["GET"])
def admin_get_bot_config():
    try:
        return jsonify({"ok": True, "config": km.get_bot_config()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/bot-config", methods=["PUT"])
def admin_update_bot_config():
    # Acepta cualquier subconjunto de: enabled, chat_id, mensaje_encabezado, mensaje_sin_diagnostico
    d = request.get_json(silent=True) or {}
    try:
        cfg = km.update_bot_config(d)
        return jsonify({"ok": True, "config": cfg})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# PUNTO DE ENTRADA
# Ejecutar con: python app.py
# El servidor queda escuchando en http://localhost:5000
# ============================================================
if __name__ == "__main__":
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
