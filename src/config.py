import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

MODEL_NAME = os.getenv("MODEL_NAME", "gemma-4-26b-a4b-it-uncensored")

# Whitelist: comma-separated user IDs. Empty = open to everyone.
_raw = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS: set[int] = (
    {int(uid.strip()) for uid in _raw.split(",") if uid.strip()}
    if _raw.strip()
    else set()
)