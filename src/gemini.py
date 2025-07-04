# This is the main logic for the Gemini Pro Telegram bot.
import logging
from pyrofork import Client, filters
from google.generativeai import generate_text, generate_image
from .config import API_ID, API_HASH, GOOGLE_API_KEY, BOT_TOKEN

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the bot client
bot = Client("GeminiProBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command("gem"))
def handle_text_prompt(client, message):
    prompt = message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else ""
    if prompt:
        response = generate_text(prompt, api_key=GOOGLE_API_KEY)
        message.reply(response.text)
    else:
        message.reply("Please provide a prompt after the command.")

@bot.on_message(filters.photo & filters.reply)
def handle_image_prompt(client, message):
    prompt = message.reply_to_message.text if message.reply_to_message else ""
    image_file = message.photo.file_id
    image_path = bot.download_media(image_file)
    response = generate_image(image_path, prompt, api_key=GOOGLE_API_KEY)
    message.reply(response.url)

if __name__ == "__main__":
    bot.run()