import logging
import google.generativeai as genai
from pyrogram import Client, filters
from PIL import Image

# 1. Importamos TODAS las variables necesarias desde config, incluyendo MODEL_NAME
from config import API_ID, API_HASH, GOOGLE_API_KEY, BOT_TOKEN, MODEL_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN Y MODELO ÚNICO DE GOOGLE ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    
    # 2. Usamos directamente la variable MODEL_NAME importada desde config.py
    model = genai.GenerativeModel(MODEL_NAME)
    
    # 3. El log ahora muestra el modelo que se cargó desde la configuración.
    logger.info(f"Modelo de Gemini cargado exitosamente: {MODEL_NAME}")
    
except Exception as e:
    logger.critical(f"No se pudo configurar la API de Google. Verifica tu GOOGLE_API_KEY. Error: {e}")
    # Si no podemos configurar el modelo, no tiene sentido continuar.
    exit()

# Inicializa el bot de Telegram
bot = Client("GeminiProBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("gem"))
def handle_text_prompt(client, message):
    prompt = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if not prompt:
        message.reply("Por favor, escribe un prompt después del comando. Ejemplo: `/gem ¿Cuál es la capital de Mongolia?`")
        return

    try:
        processing_message = message.reply("⚙️ Procesando tu petición...")
        response = model.generate_content(prompt)
        processing_message.edit_text(response.text)
    except Exception as e:
        logger.error(f"Error en handle_text_prompt: {e}")
        processing_message.edit_text(f"❌ Ocurrió un error al procesar tu petición:\n\n`{str(e)}`")

@bot.on_message(filters.command(["imgai", "img"]) & filters.reply)
def handle_image_prompt(client, message):
    replied_message = message.reply_to_message
    if not replied_message or not replied_message.photo:
        message.reply("Por favor, usa este comando respondiendo a una imagen.")
        return

    prompt_parts = message.text.split(" ", 1)
    prompt = prompt_parts[1] if len(prompt_parts) > 1 else "Describe detalladamente lo que ves en esta imagen."
    
    try:
        processing_message = message.reply("🖼️ Analizando la imagen con tu prompt...")
        image_path = bot.download_media(replied_message.photo.file_id)
        img = Image.open(image_path)
        
        # Le pasamos el prompt y la imagen al mismo modelo multimodal
        response = model.generate_content([prompt, img])
        
        processing_message.edit_text(response.text)
    except Exception as e:
        logger.error(f"Error en handle_image_prompt: {e}")
        processing_message.edit_text(f"❌ Ocurrió un error al analizar la imagen:\n\n`{str(e)}`")


if __name__ == "__main__":
    print("🤖 El bot se está iniciando...")
    bot.run()
    print("🛑 El bot se ha detenido.")