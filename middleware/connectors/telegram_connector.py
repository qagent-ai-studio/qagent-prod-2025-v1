import os
import logging
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

# Configuración DB
db_uri = os.environ.get("DB_URL")
engine = create_engine(db_uri)
Session = sessionmaker(bind=engine)


from dotenv import load_dotenv
load_dotenv()

QAGENT_WEBHOOK_URL = os.environ.get("QAGENT_WEBHOOK_URL") 
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") 
print("TELEGRAM_TOKEN:", TELEGRAM_TOKEN)

# Logging básico
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy QAgent. Escribe tu consulta en lenguaje natural.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    
   # Capturar el ID único del usuario de Telegram
    user_id = str(update.message.from_user.id)
    print(f"👤 Usuario ID: {user_id}")  # DEBUG

    # Consultar en base de datos si el ID está registrado
    try:
        session = Session()
        result = session.execute(
            text("SELECT 1 FROM users WHERE identifier = :user_id LIMIT 1"),
            {"user_id": user_id}
        ).fetchone()

        if not result:
            await update.message.reply_text("⚠️ Tu usuario no está autorizado para usar este bot. Por favor Contacta al administrador.")
            return

    except Exception as e:
        print(f"❌ Error consultando acceso en DB: {e}")
        await update.message.reply_text("⚠️ Error al validar acceso. Intenta más tarde o contacta al admin.")
        return
    finally:
        session.close()

    # Usamos el ID como identificador del usuario para el backend
    usuario = user_id
    
    pregunta = update.message.text
    usuario = update.message.from_user.username or str(update.message.from_user.id)
    # Envía a QAgent
    payload = {
        "usuario": usuario,
        "mensaje": f"TELEGRAM_MSN:{pregunta}"
    }
    respuesta = "Sin respuesta del agente."
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(QAGENT_WEBHOOK_URL, json=payload) as resp:
                data = await resp.json()
                respuesta = data.get("respuesta", "Sin respuesta del agente.")
    except Exception as e:
        respuesta = f"Error consultando al agente: {e}"
        logging.error(respuesta)
    await update.message.reply_text(respuesta)

def main():
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN.strip() == "":
        print("❌ ERROR: La variable TELEGRAM_TOKEN no está definida o está vacía. Pon tu token de BotFather en el .env.")
        exit(1)
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
    
    
# comando desde el root del proyecto
# python middleware/connectors/telegram_connector.py