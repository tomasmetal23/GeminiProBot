import os

API_ID = os.getenv("API_ID", "")
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Esta es ahora la única fuente de verdad para el nombre del modelo.
# Si MODEL_NAME no está en el .env, usará 'gemini-1.5-flash-latest' por defecto.
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash-latest") 