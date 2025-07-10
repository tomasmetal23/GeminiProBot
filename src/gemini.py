import logging
import google.generativeai as genai
from pyrogram import Client, filters
from PIL import Image

# 1. Importamos TODAS las variables necesarias desde config, incluyendo MODEL_NAME
from config import API_ID, API_HASH, GOOGLE_API_KEY, BOT_TOKEN, MODEL_NAME

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- NUEVA FUNCIÓN PARA MANEJAR TEXTOS LARGOS ---
def send_long_message(message, text):
    """
    Divide un texto largo en trozos de 4096 caracteres y los envía como mensajes separados,
    respondiendo al mensaje original del usuario.
    """
    MAX_LENGTH = 4096
    
    # Dividimos el texto en trozos del tamaño máximo permitido
    for i in range(0, len(text), MAX_LENGTH):
        chunk = text[i:i + MAX_LENGTH]
        # Usamos message.reply() para que cada parte responda al mensaje original del usuario
        message.reply(chunk, disable_web_page_preview=True)

# --- CONFIGURACIÓN Y MODELO ÚNICO DE GOOGLE ---
try:
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
    logger.info(f"Modelo de Gemini cargado exitosamente: {MODEL_NAME}")
except Exception as e:
    logger.critical(f"No se pudo configurar la API de Google. Verifica tu GOOGLE_API_KEY. Error: {e}")
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
        
        # --- LÓGICA MEJORADA PARA ENVIAR LA RESPUESTA ---
        if len(response.text) <= 4096:
            # Si el mensaje es corto, editamos el mensaje original.
            processing_message.edit_text(response.text)
        else:
            # Si el mensaje es largo, borramos "Procesando..." y usamos nuestra nueva función.
            processing_message.delete()
            send_long_message(message, response.text)
            
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
        response = model.generate_content([prompt, img])
        
        # --- APLICAMOS LA MISMA LÓGICA MEJORADA AQUÍ ---
        if len(response.text) <= 4096:
            processing_message.edit_text(response.text)
        else:
            processing_message.delete()
            send_long_message(message, response.text)

    except Exception as e:
        logger.error(f"Error en handle_image_prompt: {e}")
        processing_message.edit_text(f"❌ Ocurrió un error al analizar la imagen:\n\n`{str(e)}`")


if __name__ == "__main__":
    print("🤖 El bot se está iniciando...")
    bot.run()
    print("🛑 El bot se ha detenido.")