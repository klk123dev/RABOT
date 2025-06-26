import requests
import time
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "PEGA_AQUÍ_T7220704086:AAHIooBbtT-Tei70ZodcsJY35RdE-Vp-oTA"  # 👈 El de @BotFather
bot = Bot(token=TOKEN)

# Diccionario para guardar eventos a monitorear: {chat_id: url}
monitored_events = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎟️ **Monitor de Eventos RA**\n\n"
        "Envía la URL de un evento SOLD OUT y lo monitorearé cada 5 segundos.\n"
        "Ejemplo:\n"
        "https://www.residentadvisor.net/events/123456"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id
    
    if not url.startswith("http"):
        await update.message.reply_text("⚠️ ¡URL inválida! Envía un enlace como: https://www.residentadvisor.net/events/123456")
        return
    
    monitored_events[chat_id] = url
    await update.message.reply_text(f"🔍 Monitoreando evento:\n{url}\n\nTe avisaré cuando haya entradas disponibles!")
    
    # Inicia el monitoreo en segundo plano
    import threading
    threading.Thread(target=check_availability, args=(chat_id, url)).start()

def check_availability(chat_id: int, url: str):
    while chat_id in monitored_events:  # Mientras siga activo
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            # Detección mejorada (2025)
            if "tickets for this event are sold out" not in response.text.lower() and "sold out" not in response.text.lower():
                bot.send_message(
                    chat_id=chat_id,
                    text=f"🚨 ¡ENTRADAS DISPONIBLES! 🎟️\n{url}"
                )
                del monitored_events[chat_id]  # Deja de monitorear
                break
                
            time.sleep(5)  # Revisa cada 5 segundos
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

# Configuración del bot
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Inicia el bot
print("🤖 Bot iniciado! Usa /start en Telegram")
application.run_polling()