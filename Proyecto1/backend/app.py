import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import prolog_interface
import history_manager
import telegram_service
import knowledge_manager as km
from config import FLASK_PORT, FLASK_DEBUG

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "..", "frontend", "templates"),
    static_folder=os.path.join(BASE_DIR, "..", "frontend", "static")
)

# Permite peticiones desde el frontend (origen diferente al del backend)
CORS(app)


# ============================================================
# ENDPOINT: GET /api/sintomas
# Devuelve la lista completa de sintomas disponibles para que
# el frontend pueda construir el formulario de seleccion.
# ============================================================
@app.route("/api/sintomas", methods=["GET"])
def get_sintomas():
    try:
        sintomas = prolog_interface.obtener_sintomas()
        return jsonify({"ok": True, "sintomas": sintomas})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ENDPOINT: POST /api/diagnostico
# Recibe la lista de sintomas seleccionados por el usuario,
# consulta Prolog, guarda en historial y notifica por Telegram.
#
# Body JSON esperado: { "sintomas": ["pantalla_negra", "ruido_disco"] }
# ============================================================
@app.route("/api/diagnostico", methods=["POST"])
def post_diagnostico():
    datos = request.get_json(silent=True)

    if not datos or "sintomas" not in datos:
        return jsonify({"ok": False, "error": "Se requiere el campo 'sintomas'"}), 400

    sintomas = datos["sintomas"]

    if not isinstance(sintomas, list) or len(sintomas) == 0:
        return jsonify({"ok": False, "error": "'sintomas' debe ser una lista no vacia"}), 400

    try:
        diagnosticos = prolog_interface.obtener_diagnostico(sintomas)

        # Persiste el resultado independientemente de si hay diagnosticos o no
        entrada = history_manager.guardar_diagnostico(sintomas, diagnosticos)

        # El envio a Telegram es no bloqueante: si falla no afecta la respuesta
        telegram_service.enviar_notificacion(sintomas, diagnosticos)

        return jsonify({
            "ok": True,
            "id": entrada["id"],
            "timestamp": entrada["timestamp"],
            "sintomas": sintomas,
            "diagnosticos": diagnosticos
        })

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ENDPOINT: GET /api/historial
# Devuelve todos los diagnosticos realizados, del mas reciente
# al mas antiguo.
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
# Devuelve un diagnostico especifico por su ID unico.
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


@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# ADMIN - SINTOMAS
# ============================================================
@app.route("/api/admin/sintomas", methods=["GET"])
def admin_get_sintomas():
    try:
        return jsonify({"ok": True, "sintomas": km.get_sintomas()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/sintomas", methods=["POST"])
def admin_add_sintoma():
    d = request.get_json(silent=True) or {}
    if not d.get("id") or not d.get("descripcion"):
        return jsonify({"ok": False, "error": "Se requieren 'id' y 'descripcion'"}), 400
    try:
        km.add_sintoma(d["id"].strip(), d["descripcion"].strip())
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 409
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/sintomas/<sid>", methods=["PUT"])
def admin_update_sintoma(sid):
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
    try:
        km.delete_sintoma(sid)
        return jsonify({"ok": True})
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - FALLAS
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
# ============================================================
@app.route("/api/admin/recomendaciones", methods=["GET"])
def admin_get_recs():
    try:
        return jsonify({"ok": True, "recomendaciones": km.get_recomendaciones()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/recomendaciones/<fault_id>", methods=["PUT"])
def admin_update_recs(fault_id):
    d = request.get_json(silent=True) or {}
    if "lista" not in d or not isinstance(d["lista"], list):
        return jsonify({"ok": False, "error": "Se requiere 'lista' (array)"}), 400
    try:
        km.update_recomendaciones(fault_id, d["lista"])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ============================================================
# ADMIN - REGLAS
# ============================================================
@app.route("/api/admin/reglas", methods=["GET"])
def admin_get_reglas():
    try:
        return jsonify({"ok": True, "reglas": km.get_reglas()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/reglas", methods=["POST"])
def admin_add_regla():
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
# ADMIN - CONFIGURACION DEL BOT
# ============================================================
@app.route("/api/admin/bot-config", methods=["GET"])
def admin_get_bot_config():
    try:
        return jsonify({"ok": True, "config": km.get_bot_config()})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/api/admin/bot-config", methods=["PUT"])
def admin_update_bot_config():
    d = request.get_json(silent=True) or {}
    try:
        cfg = km.update_bot_config(d)
        return jsonify({"ok": True, "config": cfg})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=FLASK_PORT, debug=FLASK_DEBUG)
