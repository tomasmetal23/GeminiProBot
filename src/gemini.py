import logging
import base64
import os
from openai import OpenAI
from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOKEN, MODEL_NAME

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONEXIÓN A LM STUDIO (7900 XT via OpenAI API) ---
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:11434/v1")
client_ai = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")


def encode_image(image_path):
    """Convierte una imagen a Base64 para enviarla a LM Studio."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def send_long_message(message, text):
    """Divide textos largos en chunks de 4096 caracteres y los envía respondiendo al original."""
    MAX_LENGTH = 4096
    for i in range(0, len(text), MAX_LENGTH):
        message.reply(text[i : i + MAX_LENGTH], disable_web_page_preview=True)


# Inicializa el bot de Telegram
bot = Client("GemmaLocalBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# --- COMANDO DE TEXTO ---
@bot.on_message(filters.command("gem"))
def handle_text_prompt(client, message):
    parts = message.text.split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else ""
    if not prompt:
        message.reply(
            "Por favor, escribe un prompt después del comando. Ejemplo: `/gem ¿Cuál es la capital de Mongolia?`"
        )
        return

    processing_message = None
    try:
        processing_message = message.reply("⚙️ Generando con Gemma local...")
        response = client_ai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
        )
        answer = response.choices[0].message.content

        if len(answer) <= 4096:
            processing_message.edit_text(answer)
        else:
            processing_message.delete()
            send_long_message(message, answer)

    except Exception as e:
        logger.error(f"Error en handle_text_prompt: {e}")
        if processing_message:
            processing_message.edit_text(
                f"❌ Error al generar respuesta:\n\n`{str(e)}`"
            )
        else:
            message.reply(f"❌ Error al generar respuesta:\n\n`{str(e)}`")


# --- COMANDO DE IMAGEN (requiere modelo Vision cargado en LM Studio) ---
@bot.on_message(filters.command(["imgai", "img"]) & filters.reply)
def handle_image_prompt(client, message):
    replied = message.reply_to_message
    if not replied or not replied.photo:
        message.reply("Por favor, usa este comando respondiendo a una imagen.")
        return

    parts = message.text.split(" ", 1)
    prompt = parts[1] if len(parts) > 1 else "Describe detalladamente lo que ves en esta imagen."

    processing_message = None
    path = None
    try:
        processing_message = message.reply("🖼️ Analizando imagen localmente...")
        path = bot.download_media(replied.photo.file_id)
        base64_image = encode_image(path)

        response = client_ai.chat.completions.create(
            model=MODEL_NAME,  # ¡OJO! Necesita un modelo Vision cargado en LM Studio
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        answer = response.choices[0].message.content

        if len(answer) <= 4096:
            processing_message.edit_text(answer)
        else:
            processing_message.delete()
            send_long_message(message, answer)

    except Exception as e:
        logger.error(f"Error en handle_image_prompt: {e}")
        err_msg = f"❌ Error de visión: `{str(e)}`\n\n_(¿Tienes un modelo Vision cargado en LM Studio?)_"
        if processing_message:
            processing_message.edit_text(err_msg)
        else:
            message.reply(err_msg)
    finally:
        if path and os.path.exists(path):
            os.remove(path)


if __name__ == "__main__":
    print(f"🤖 Bot iniciando con modelo local: {MODEL_NAME}")
    print("🔗 Conectando a LM Studio en http://localhost:11434/v1")
    bot.run()
    print("🛑 El bot se ha detenido.")