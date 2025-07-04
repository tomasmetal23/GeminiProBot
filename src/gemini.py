import logging
import google.generativeai as genai
from pyrogram import Client, filters
from PIL import Image  # Necesario para manejar la imagen
from config import API_ID, API_HASH, GOOGLE_API_KEY, BOT_TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE LA API DE GOOGLE ---
# Así es como se configura la API key ahora
genai.configure(api_key=GOOGLE_API_KEY)

# --- CREACIÓN DE LOS MODELOS ---
# Es más eficiente crear los modelos una sola vez
# Modelo para texto
text_model = genai.GenerativeModel('gemini-1.5-flash-latest') # Usamos el modelo más reciente y rápido
# Modelo para visión (texto + imagen)
vision_model = genai.GenerativeModel('gemini-pro-vision')

# Inicializa el bot de Telegram
bot = Client("GeminiProBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("gem"))
def handle_text_prompt(client, message):
    # Extrae el prompt del comando
    prompt = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    
    if not prompt:
        message.reply("Por favor, escribe un prompt después del comando. Ejemplo: `/gem ¿Cuál es la capital de Mongolia?`")
        return

    try:
        # Muestra un mensaje de "procesando..."
        processing_message = message.reply("⚙️ Procesando tu petición...")
        
        # --- NUEVA FORMA DE LLAMAR A LA API DE TEXTO ---
        response = text_model.generate_content(prompt)
        
        # Edita el mensaje de "procesando" con la respuesta final
        processing_message.edit_text(response.text)
        
    except Exception as e:
        logger.error(f"Error en handle_text_prompt: {e}")
        message.reply(f"❌ Ocurrió un error al procesar tu petición:\n\n`{str(e)}`")

@bot.on_message(filters.photo & filters.reply)
def handle_image_prompt(client, message):
    # La imagen debe ser una respuesta a un mensaje de texto que será el prompt
    if not message.reply_to_message or not message.reply_to_message.text:
        message.reply("Por favor, responde con una imagen a un mensaje de texto que contenga el prompt.")
        return

    prompt = message.reply_to_message.text
    
    try:
        processing_message = message.reply("🖼️ Analizando la imagen...")

        # Descarga la imagen
        image_path = bot.download_media(message.photo.file_id)
        
        # Abre la imagen con Pillow
        img = Image.open(image_path)

        # --- NUEVA FORMA DE LLAMAR A LA API DE VISIÓN ---
        # Se envía una lista con el texto y la imagen
        response = vision_model.generate_content([prompt, img])
        
        # Edita el mensaje de "procesando" con la respuesta final
        processing_message.edit_text(response.text)

    except Exception as e:
        logger.error(f"Error en handle_image_prompt: {e}")
        message.reply(f"❌ Ocurrió un error al analizar la imagen:\n\n`{str(e)}`")


if __name__ == "__main__":
    print("🤖 El bot se está iniciando...")
    bot.run()
    print("🛑 El bot se ha detenido.")