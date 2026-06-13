import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BOT_CONFIG_FILE


def _get_config():
    try:
        with open(BOT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"enabled": True, "mensaje_sin_diagnostico": "Sin diagnostico.", "mensaje_encabezado": "Doctor Byte"}


def _escapar_html(texto):
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _formatear_mensaje(sintomas, diagnosticos):
    cfg = _get_config()
    encabezado = cfg.get("mensaje_encabezado", "Doctor Byte - Nuevo Diagnostico")
    msg_sin_diag = cfg.get("mensaje_sin_diagnostico", "No se encontro diagnostico.")

    lineas = [f"<b>{_escapar_html(encabezado)}</b>\n"]

    lineas.append("<b>Sintomas reportados:</b>")
    for s in sintomas:
        lineas.append(f"  - {_escapar_html(s.replace('_', ' '))}")

    lineas.append("\n<b>Diagnosticos encontrados:</b>")

    if not diagnosticos:
        lineas.append(f"  {_escapar_html(msg_sin_diag)}")
    else:
        for d in diagnosticos:
            lineas.append(f"\n<b>Falla:</b> {_escapar_html(d['descripcion'])}")
            lineas.append("<b>Recomendaciones:</b>")
            for rec in d["recomendaciones"]:
                lineas.append(f"  - {_escapar_html(rec)}")

    return "\n".join(lineas)


def enviar_notificacion(sintomas, diagnosticos):
    cfg = _get_config()

    if not cfg.get("enabled", True):
        print("[Telegram] Bot desactivado, se omite la notificacion.")
        return False

    chat_id = cfg.get("chat_id", "").strip() or TELEGRAM_CHAT_ID

    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("[Telegram] Token o chat_id no configurados.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": _formatear_mensaje(sintomas, diagnosticos),
        "parse_mode": "HTML"
    }

    try:
        respuesta = requests.post(url, json=payload, timeout=10)
        if respuesta.status_code == 200:
            return True
        print(f"[Telegram] Error {respuesta.status_code}: {respuesta.text}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"[Telegram] Excepcion: {e}")
        return False
