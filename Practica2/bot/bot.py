import logging
import os
import time

import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_URL            = os.getenv("API_URL", "http://backend:8000")


# ── API helpers ────────────────────────────────────────────
def wait_for_backend(retries: int = 15, delay: int = 5) -> bool:
    for i in range(retries):
        try:
            r = requests.get(f"{API_URL}/health", timeout=5)
            if r.status_code == 200:
                logger.info("Backend listo.")
                return True
        except Exception:
            pass
        logger.info(f"Esperando backend… ({i + 1}/{retries})")
        time.sleep(delay)
    return False


def query_api(text: str, user: str, user_id: str) -> dict:
    r = requests.post(
        f"{API_URL}/api/bot/query",
        json={"query": text, "telegram_user": user, "telegram_user_id": user_id},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def get_categories() -> list:
    r = requests.get(f"{API_URL}/api/categories/", timeout=10)
    r.raise_for_status()
    return r.json()


# ── Handlers ───────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! 👋 Soy *SmartBot*, tu asistente de consultas frecuentes.\n\n"
        "Escríbeme cualquier pregunta y buscaré la mejor respuesta en nuestra base de datos.\n\n"
        "Comandos disponibles:\n"
        "/start — Iniciar el bot\n"
        "/help — Mostrar ayuda\n"
        "/categorias — Ver categorías de información disponibles",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*SmartBot* — Ayuda\n\n"
        "Simplemente escribe tu pregunta en lenguaje natural y responderé con "
        "la información que tengo registrada.\n\n"
        "Si no encuentro una respuesta te lo haré saber para que puedas "
        "consultar directamente con el área correspondiente.",
        parse_mode="Markdown",
    )


async def cmd_categorias(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cats = get_categories()
        if not cats:
            await update.message.reply_text("No hay categorías registradas aún.")
            return
        lines = ["*Categorías disponibles:*\n"]
        for c in cats:
            lines.append(f"• *{c['name']}*")
            if c.get("description"):
                lines.append(f"  _{c['description']}_")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error al obtener categorías: {e}")
        await update.message.reply_text("Error al obtener las categorías. Intenta más tarde.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user    = update.message.from_user
    text    = update.message.text or ""
    uname   = user.username or user.first_name or str(user.id)
    user_id = str(user.id)

    try:
        result = query_api(text, uname, user_id)
        if result.get("found") and result.get("answer"):
            await update.message.reply_text(result["answer"])
        else:
            await update.message.reply_text(
                "Lo siento, no tengo una respuesta registrada para esa consulta. 🙁\n"
                "Te recomiendo contactar directamente con el área correspondiente."
            )
    except Exception as e:
        logger.error(f"Error al procesar consulta '{text[:50]}': {e}")
        await update.message.reply_text(
            "Ocurrió un error al procesar tu consulta. Por favor intenta de nuevo."
        )


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comando no reconocido. Usa /help para ver los comandos disponibles."
    )


# ── Main ───────────────────────────────────────────────────
def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN no está configurado. Saliendo.")
        return

    if not wait_for_backend():
        logger.error("No se pudo conectar con el backend. Saliendo.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",      cmd_start))
    app.add_handler(CommandHandler("help",       cmd_help))
    app.add_handler(CommandHandler("categorias", cmd_categorias))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("SmartBot iniciado. Esperando mensajes…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
