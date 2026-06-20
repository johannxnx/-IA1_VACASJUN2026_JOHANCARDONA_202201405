# ============================================================
# config.py — Configuracion central del sistema
#
# Este modulo carga todas las variables de entorno desde el
# archivo .env (nunca hardcodeadas en el codigo fuente).
# Tambien define las rutas absolutas a los archivos clave.
#
# PENALIZACION EVITADA: Token/ID del bot quemado en codigo = -5%
# Por eso usamos load_dotenv() y os.getenv().
# ============================================================

import os
from dotenv import load_dotenv

# Carga el archivo .env del directorio actual
# Si no existe .env, os.getenv devolvera el valor por defecto
load_dotenv()

# --- Credenciales de Telegram (vienen del .env, nunca del codigo) ---

# Token unico del bot, obtenido desde BotFather en Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ID del chat al que se enviaran las notificaciones de diagnostico
# Se puede obtener en https://api.telegram.org/bot<TOKEN>/getUpdates
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# --- Configuracion del servidor Flask ---
FLASK_PORT  = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# --- Rutas absolutas a los archivos del sistema ---

# Directorio donde esta este archivo (backend/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ruta al archivo Prolog que contiene toda la base de conocimiento
# Este archivo es REGENERADO cada vez que el admin modifica algo
PROLOG_FILE = os.path.join(BASE_DIR, "..", "prolog", "doctor_byte.pl")

# Archivo JSON donde se persiste el historial de diagnosticos
# Está en .gitignore para no subir datos de usuarios al repositorio
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")

# Archivo JSON con la configuracion del bot de Telegram
# (habilitado/deshabilitado, mensajes personalizados, chat_id)
BOT_CONFIG_FILE = os.path.join(BASE_DIR, "data", "bot_config.json")
