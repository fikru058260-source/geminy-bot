import os
import logging
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from flask import Flask
import threading

# የሎግ መረጃዎችን በግልጽ Render ላይ ለማሳየት
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

server = Flask('')

@server.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render የሚሰጠውን dynamic port ለመጠቀም
    port = int(os.environ.get('PORT', 8080))
    server.run(host='0.0.0.0', port=port)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    logger.error("እባክዎ TELEGRAM_TOKEN እና GEMINI_API_KEY በሊንክ መሙላትዎን ያረጋግጡ!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! እኔ የእርስዎ የ AI ረዳት ነኝ። እንዴት ልርዳዎት?")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = model.generate_content(f"አንተ የኢትዮጵያ ንግድ ረዳት ነህ። በአማርኛ በትህትና መልስ ስጥ። ጥያቄ፡ {update.message.text}")
        await update.message.reply_text(response.text)
    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        await update.message.reply_text("ይቅርታ፣ አሁን ላይ መመለስ አልቻልኩም።")

def main():
    try:
        # Flask ሰርቨሩን በሌላ Thread ማስነሳት
        threading.Thread(target=run_flask, daemon=True).start()
        
        logger.info("ቦቱ መነሳት ጀምሯል...")
        app = Application.builder().token(TELEGRAM_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # ቦቱ ስራ እንዲጀምር
        app.run_polling()
    except Exception as e:
        logger.error(f"Critical Error in main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

