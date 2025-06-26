import requests
import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from flask import Flask
import threading

# Configuración
TOKEN = "7220704086:AAHIooBbtT-Tei70ZodcsJY35RdE-Vp-oTA"  # 👈 Reemplaza con tu token real
monitored_events = {}  # {chat_id: url}

# Configura logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---- COMANDOS DEL BOT ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mensaje de bienvenida"""
    await update.message.reply_text(
        "🎟️ **Monitor de Eventos RA**\n\n"
        "Envía la URL de un evento SOLD OUT y lo monitorearé cada 5 segundos.\n"
        "Ejemplo:\n"
        "https://www.residentadvisor.net/events/123456"
    )

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestiona URLs enviadas por el usuario"""
    chat_id = update.message.chat_id
    url = update.message.text.strip()
    
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text("⚠️ ¡URL inválida! Debe comenzar con http:// o https://")
        return
    
    monitored_events[chat_id] = url
    await update.message.reply_text(
        f"🔍 **Monitoreando evento:**\n{url}\n\n"
        "Te notificaré en cuanto detecte entradas disponibles!"
    )
    
    # Inicia monitoreo en segundo plano
    threading.Thread(target=check_availability, args=(chat_id, url), daemon=True).start()

# ---- MONITOREO EN TIEMPO REAL ----
def check_availability(chat_id: int, url: str):
    """Verifica disponibilidad cada 5 segundos"""
    bot = Bot(token=TOKEN)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    while chat_id in monitored_events:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # Detección mejorada (2025)
            if all(
                keyword not in response.text.lower() 
                for keyword in ["sold out", "agotado", "no tickets"]
            ):
                asyncio.run(
                    bot.send_message(
                        chat_id=chat_id,
                        text=f"🚨 **¡ENTRADAS DISPONIBLES!** 🎟️\n{url}"
                    )
                )
                del monitored_events[chat_id]
                break
                
            time.sleep(5)  # Espera 5 segundos
            
        except Exception as e:
            logger.error(f"Error al monitorear {url}: {str(e)}")
            time.sleep(10)

# ---- CONFIGURACIÓN DEL BOT ----
def main():
    """Configura e inicia el bot"""
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .http_version("1.1")
        .build()
    )
    
    # Manejadores
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    
    # Inicia Flask para Render (opcional)
    flask_thread = threading.Thread(
        target=lambda: Flask(__name__).run(host='0.0.0.0', port=10000),
        daemon=True
    )
    flask_thread.start()
    
    logger.info("🤖 Bot iniciado correctamente")
    application.run_polling(
        close_loop=False,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
