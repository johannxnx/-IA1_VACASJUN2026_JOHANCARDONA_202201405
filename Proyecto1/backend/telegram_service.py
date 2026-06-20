# ============================================================
# telegram_service.py — Notificaciones via Bot de Telegram
#
# Envia un mensaje al chat configurado cada vez que el usuario
# realiza un diagnostico (con o sin resultado).
#
# DISEÑO NO BLOQUEANTE:
#   Si el envio falla (sin internet, token invalido, bot
#   desactivado), el error se registra en consola pero NO
#   interrumpe la respuesta al usuario.
#
# SEGURIDAD:
#   El TOKEN nunca esta en este archivo. Se lee desde config.py
#   que a su vez lo carga del .env. Evita penalizacion de -5%.
#
# CONFIGURACION DINAMICA:
#   El admin puede cambiar mensajes y chat_id desde el panel web.
#   Estos valores se leen de bot_config.json en cada envio.
#   El chat_id del JSON tiene prioridad sobre el del .env.
# ============================================================

import json
import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BOT_CONFIG_FILE


def _get_config():
    """
    Lee la configuracion actual del bot desde bot_config.json.
    Si el archivo no existe o esta corrupto, usa valores por defecto.
    """
    try:
        with open(BOT_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Valores por defecto si no existe el archivo
        return {
            "enabled": True,
            "chat_id": "",
            "mensaje_sin_diagnostico": "Sin diagnostico.",
            "mensaje_encabezado": "Doctor Byte"
        }


def _escapar_html(texto):
    """
    Escapa caracteres especiales de HTML para el parse_mode='HTML' de Telegram.
    Sin esto, caracteres como < > & rompen el formato del mensaje.

    Usamos HTML en vez de Markdown porque Markdown fallaba con textos
    que contienen guiones bajos (nombres de variables Prolog como fallo_ram).
    """
    return texto.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _formatear_mensaje(sintomas, diagnosticos):
    """
    Construye el texto del mensaje de Telegram con formato HTML.

    Estructura del mensaje:
      <b>Doctor Byte - Nuevo Diagnostico</b>

      <b>Sintomas reportados:</b>
        - pantalla negra
        - ruido de disco

      <b>Diagnosticos encontrados:</b>

      <b>Falla:</b> Fallo en el disco duro...
      <b>Recomendaciones:</b>
        - Realizar respaldo...
        - Reemplazar el disco...
    """
    cfg = _get_config()
    encabezado  = cfg.get("mensaje_encabezado", "Doctor Byte - Nuevo Diagnostico")
    msg_sin_diag = cfg.get("mensaje_sin_diagnostico", "No se encontro diagnostico.")

    lineas = [f"<b>{_escapar_html(encabezado)}</b>\n"]

    # Lista de sintomas reportados (con guion bajo convertido a espacio)
    lineas.append("<b>Sintomas reportados:</b>")
    for s in sintomas:
        lineas.append(f"  - {_escapar_html(s.replace('_', ' '))}")

    lineas.append("\n<b>Diagnosticos encontrados:</b>")

    if not diagnosticos:
        # Caso sin diagnostico: mensaje personalizable desde el admin
        lineas.append(f"  {_escapar_html(msg_sin_diag)}")
    else:
        # Caso con diagnostico: mostramos falla y recomendaciones
        for d in diagnosticos:
            lineas.append(f"\n<b>Falla:</b> {_escapar_html(d['descripcion'])}")
            lineas.append("<b>Recomendaciones:</b>")
            for rec in d["recomendaciones"]:
                lineas.append(f"  - {_escapar_html(rec)}")

    return "\n".join(lineas)


def enviar_notificacion(sintomas, diagnosticos):
    """
    Envia la notificacion de diagnostico al chat de Telegram configurado.

    Parametros:
        sintomas    (list[str]): IDs de los sintomas seleccionados
        diagnosticos (list[dict]): Resultado del diagnostico de Prolog

    Retorna:
        bool: True si el envio fue exitoso, False en cualquier otro caso

    El chat_id se resuelve en este orden de prioridad:
      1. El valor en bot_config.json (modificable desde el admin)
      2. El valor en .env (TELEGRAM_CHAT_ID)
    """
    cfg = _get_config()

    # Si el bot esta desactivado desde el panel admin, no enviamos nada
    if not cfg.get("enabled", True):
        print("[Telegram] Bot desactivado, se omite la notificacion.")
        return False

    # Resolucion del chat_id: JSON tiene prioridad sobre .env
    chat_id = cfg.get("chat_id", "").strip() or TELEGRAM_CHAT_ID

    # Validamos que tengamos tanto el token como el destino
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print("[Telegram] Token o chat_id no configurados.")
        return False

    # Endpoint de la API de Telegram para enviar mensajes
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id":    chat_id,
        "text":       _formatear_mensaje(sintomas, diagnosticos),
        "parse_mode": "HTML"   # HTML porque Markdown falla con caracteres Prolog
    }

    try:
        respuesta = requests.post(url, json=payload, timeout=10)
        if respuesta.status_code == 200:
            return True
        # Error de la API (token invalido, chat no encontrado, etc.)
        print(f"[Telegram] Error {respuesta.status_code}: {respuesta.text}")
        return False
    except requests.exceptions.RequestException as e:
        # Error de red (sin internet, timeout, etc.)
        print(f"[Telegram] Excepcion de red: {e}")
        return False
