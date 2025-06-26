import requests
import time
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder
import logging

# Configuración anti-conflictos
application = (
    ApplicationBuilder()
    .token("7220704086:AAHIooBbtT-Tei70ZodcsJY35RdE-Vp-oTA")  # ← Usa tu token real
    .concurrent_updates(True)  # Permite múltiples solicitudes
    .http_version("1.1")
    .get_updates_http_version("1.1")
    .build()
)

# Configura logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot activado correctamente ✅")

# Añade tus handlers
application.add_handler(CommandHandler("start", start))

# Inicia el bot con esta configuración
application.run_polling(
    close_loop=False,
    stop_signals=None,
    drop_pending_updates=True  # Ignora mensajes pendientes
)
