import os
from dotenv import load_dotenv

load_dotenv()

# Token del bot de Telegram obtenido desde BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ID del chat al que se enviaran las notificaciones de diagnostico
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Ruta absoluta al archivo Prolog, relativa a la ubicacion de este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROLOG_FILE = os.path.join(BASE_DIR, "..", "prolog", "doctor_byte.pl")

# Archivo JSON donde se guarda el historial de diagnosticos
HISTORY_FILE = os.path.join(BASE_DIR, "data", "history.json")

BOT_CONFIG_FILE = os.path.join(BASE_DIR, "data", "bot_config.json")
