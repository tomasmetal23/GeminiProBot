"""
gemini.py — GemmaProBot main entry point.
Full async rewrite with: streaming, conversation memory, web search,
document analysis, custom system prompts, whitelist, and status check.
"""
__version__ = "2.0.0"  # local-gemma branch — full async rewrite
import asyncio
import base64
import logging
import os
import time

import pdfplumber
from openai import AsyncOpenAI
from pyrogram import Client, filters
from pyrogram.types import Message

import memory
from config import API_ID, API_HASH, BOT_TOKEN, MODEL_NAME, ALLOWED_USERS
from search import web_search

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LM Studio client (async)
# ---------------------------------------------------------------------------
LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:11434/v1")
ai = AsyncOpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio")

# ---------------------------------------------------------------------------
# Pyrogram bot (async)
# ---------------------------------------------------------------------------
bot = Client(
    "GemmaLocalBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workdir="/app/session",
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def is_allowed(user_id: int) -> bool:
    """Return True if user is whitelisted (or whitelist is empty = open)."""
    return not ALLOWED_USERS or user_id in ALLOWED_USERS


async def send_long_message(message: Message, text: str) -> None:
    """Split text into Telegram-safe chunks and reply."""
    MAX_LEN = 4096
    for i in range(0, len(text), MAX_LEN):
        await message.reply(text[i : i + MAX_LEN], disable_web_page_preview=True)


async def stream_ai_response(
    messages: list[dict],
    status_msg: Message,
) -> str:
    """
    Stream tokens from LM Studio and live-edit the Telegram message every ~40 tokens.
    Returns the full accumulated response.
    """
    full_text = ""
    token_count = 0
    last_edit_len = 0
    EDIT_EVERY = 40  # edit Telegram message every N tokens

    stream = await ai.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        full_text += delta
        token_count += 1

        # Live update every EDIT_EVERY tokens (avoid Telegram rate limits)
        if token_count % EDIT_EVERY == 0 and len(full_text) != last_edit_len:
            try:
                await status_msg.edit_text(full_text + " ▍")
                last_edit_len = len(full_text)
            except Exception:
                pass  # ignore edit errors (flood wait, etc.)

    return full_text


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("start"))
async def cmd_start(client: Client, message: Message):
    await message.reply(
        "👋 **GemmaProBot** listo!\n\n"
        "**Comandos disponibles:**\n"
        "• `/gem <prompt>` — Chat con Gemma (con memoria)\n"
        "• `/web <query>` — Busca en internet y responde con contexto\n"
        "• `/img` _(reply a foto)_ — Analiza una imagen\n"
        "• `/doc` _(reply a PDF/TXT)_ — Analiza un documento\n"
        "• `/system <prompt>` — Define tu personalidad personalizada\n"
        "• `/reset` — Borra tu historial de conversación\n"
        "• `/status` — Estado del servidor LM Studio\n"
    )


# ---------------------------------------------------------------------------
# /gem — chat with memory + streaming
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("gem"))
async def cmd_gem(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    parts = message.text.split(" ", 1)
    prompt = parts[1].strip() if len(parts) > 1 else ""
    if not prompt:
        await message.reply(
            "Escribe un prompt después del comando.\n"
            "Ejemplo: `/gem ¿Cuál es la capital de Mongolia?`"
        )
        return

    user_id = message.from_user.id
    status_msg = await message.reply("⚙️ Pensando con Gemma local...")

    try:
        system_prompt = memory.get_system_prompt(user_id)
        history = memory.get_history(user_id)

        messages = [{"role": "system", "content": system_prompt}]
        messages += history
        messages.append({"role": "user", "content": prompt})

        answer = await stream_ai_response(messages, status_msg)

        # Persist to memory
        memory.add_message(user_id, "user", prompt)
        memory.add_message(user_id, "assistant", answer)

        # Final edit with clean text
        if len(answer) <= 4096:
            await status_msg.edit_text(answer, disable_web_page_preview=True)
        else:
            await status_msg.delete()
            await send_long_message(message, answer)

    except Exception as e:
        logger.error("cmd_gem error: %s", e)
        await status_msg.edit_text(f"❌ Error al generar respuesta:\n\n`{e}`")


# ---------------------------------------------------------------------------
# /web — web search + AI response
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("web"))
async def cmd_web(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    parts = message.text.split(" ", 1)
    query = parts[1].strip() if len(parts) > 1 else ""
    if not query:
        await message.reply(
            "Escribe una búsqueda después del comando.\n"
            "Ejemplo: `/web precio del bitcoin hoy`"
        )
        return

    user_id = message.from_user.id
    status_msg = await message.reply("🌐 Buscando en internet...")

    try:
        search_results = await web_search(query)

        await status_msg.edit_text("🧠 Procesando resultados con Gemma...")

        system_prompt = memory.get_system_prompt(user_id)
        history = memory.get_history(user_id)

        context_prompt = (
            f"El usuario pregunta: {query}\n\n"
            f"Aquí tienes los resultados de búsqueda actuales como contexto:\n\n"
            f"{search_results}\n\n"
            f"Usa esta información para responder de forma precisa y actualizada."
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages += history
        messages.append({"role": "user", "content": context_prompt})

        answer = await stream_ai_response(messages, status_msg)

        memory.add_message(user_id, "user", f"[búsqueda web] {query}")
        memory.add_message(user_id, "assistant", answer)

        if len(answer) <= 4096:
            await status_msg.edit_text(answer, disable_web_page_preview=True)
        else:
            await status_msg.delete()
            await send_long_message(message, answer)

    except Exception as e:
        logger.error("cmd_web error: %s", e)
        await status_msg.edit_text(f"❌ Error en búsqueda:\n\n`{e}`")


# ---------------------------------------------------------------------------
# /img — vision analysis (reply to photo)
# ---------------------------------------------------------------------------

@bot.on_message(filters.command(["img", "imgai"]) & filters.reply)
async def cmd_img(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    replied = message.reply_to_message
    if not replied or not replied.photo:
        await message.reply("Usa este comando respondiendo a una imagen.")
        return

    parts = message.text.split(" ", 1)
    prompt = parts[1].strip() if len(parts) > 1 else "Describe detalladamente lo que ves en esta imagen."

    status_msg = await message.reply("🖼️ Analizando imagen localmente...")
    path = None

    try:
        path = await bot.download_media(replied.photo.file_id)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        response = await ai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                }
            ],
        )
        answer = response.choices[0].message.content

        if len(answer) <= 4096:
            await status_msg.edit_text(answer, disable_web_page_preview=True)
        else:
            await status_msg.delete()
            await send_long_message(message, answer)

    except Exception as e:
        logger.error("cmd_img error: %s", e)
        err = f"❌ Error de visión:\n`{e}`\n\n_(¿Tienes un modelo Vision cargado en LM Studio?)_"
        await status_msg.edit_text(err)
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------------------------
# /doc — document analysis (reply to PDF or text file)
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("doc") & filters.reply)
async def cmd_doc(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    replied = message.reply_to_message
    if not replied or not replied.document:
        await message.reply("Usa este comando respondiendo a un archivo PDF o TXT.")
        return

    doc = replied.document
    mime = doc.mime_type or ""
    file_name = doc.file_name or ""

    if "pdf" not in mime and not file_name.endswith((".pdf", ".txt", ".md")):
        await message.reply("Solo acepto archivos PDF, TXT o Markdown.")
        return

    parts = message.text.split(" ", 1)
    prompt = parts[1].strip() if len(parts) > 1 else "Resume y analiza el contenido de este documento."

    user_id = message.from_user.id
    status_msg = await message.reply("📄 Extrayendo texto del documento...")
    path = None

    try:
        path = await bot.download_media(doc.file_id)
        text_content = ""

        if file_name.endswith(".pdf") or "pdf" in mime:
            with pdfplumber.open(path) as pdf:
                pages = [p.extract_text() or "" for p in pdf.pages]
                text_content = "\n\n".join(pages)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text_content = f.read()

        if not text_content.strip():
            await status_msg.edit_text("❌ No pude extraer texto de este documento.")
            return

        # Trim to avoid exceeding context window (~8000 chars)
        MAX_DOC_CHARS = 8000
        if len(text_content) > MAX_DOC_CHARS:
            text_content = text_content[:MAX_DOC_CHARS] + "\n\n[... documento truncado ...]"

        await status_msg.edit_text("🧠 Analizando documento con Gemma...")

        system_prompt = memory.get_system_prompt(user_id)
        context_prompt = (
            f"El usuario te pide: {prompt}\n\n"
            f"Aquí está el contenido del documento:\n\n{text_content}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context_prompt},
        ]

        answer = await stream_ai_response(messages, status_msg)

        memory.add_message(user_id, "user", f"[documento: {file_name}] {prompt}")
        memory.add_message(user_id, "assistant", answer)

        if len(answer) <= 4096:
            await status_msg.edit_text(answer, disable_web_page_preview=True)
        else:
            await status_msg.delete()
            await send_long_message(message, answer)

    except Exception as e:
        logger.error("cmd_doc error: %s", e)
        await status_msg.edit_text(f"❌ Error al procesar documento:\n\n`{e}`")
    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ---------------------------------------------------------------------------
# /system — set custom system prompt
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("system"))
async def cmd_system(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    parts = message.text.split(" ", 1)
    prompt = parts[1].strip() if len(parts) > 1 else ""

    if not prompt:
        current = memory.get_system_prompt(message.from_user.id)
        await message.reply(
            f"**System prompt actual:**\n`{current}`\n\n"
            "Para cambiarlo:\n`/system Eres un asistente pirata que habla con argot marinero.`\n\n"
            "Para resetearlo al default:\n`/system reset`"
        )
        return

    if prompt.lower() == "reset":
        memory.reset_system_prompt(message.from_user.id)
        await message.reply("🔄 System prompt reseteado al valor por defecto.")
        return

    memory.set_system_prompt(message.from_user.id, prompt)
    await message.reply(f"✅ System prompt actualizado:\n`{prompt}`")


# ---------------------------------------------------------------------------
# /reset — clear conversation history
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("reset"))
async def cmd_reset(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    deleted = memory.clear_history(message.from_user.id)
    await message.reply(
        f"🗑️ Historial borrado ({deleted} mensajes eliminados).\n"
        "La próxima conversación empezará desde cero."
    )


# ---------------------------------------------------------------------------
# /status — LM Studio health check
# ---------------------------------------------------------------------------

@bot.on_message(filters.command("status"))
async def cmd_status(client: Client, message: Message):
    if not is_allowed(message.from_user.id):
        return

    status_msg = await message.reply("🔍 Comprobando estado del servidor...")

    try:
        start = time.monotonic()
        models = await ai.models.list()
        latency_ms = int((time.monotonic() - start) * 1000)

        model_names = [m.id for m in models.data] if models.data else ["(ninguno)"]
        models_list = "\n".join(f"  • `{m}`" for m in model_names)

        await status_msg.edit_text(
            f"✅ **LM Studio conectado** ({latency_ms}ms)\n\n"
            f"**Servidor:** `{LM_STUDIO_URL}`\n"
            f"**Modelo activo:** `{MODEL_NAME}`\n\n"
            f"**Modelos disponibles:**\n{models_list}"
        )
    except Exception as e:
        logger.error("cmd_status error: %s", e)
        await status_msg.edit_text(
            f"❌ **LM Studio no responde**\n\n"
            f"**URL:** `{LM_STUDIO_URL}`\n"
            f"**Error:** `{e}`\n\n"
            "_Verifica que LM Studio esté corriendo y el servidor local activo._"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    memory.init_db()
    logger.info("🤖 GemmaProBot iniciando con modelo: %s", MODEL_NAME)
    logger.info("🔗 Conectado a LM Studio: %s", LM_STUDIO_URL)
    await bot.start()
    logger.info("✅ Bot online y listo.")
    await asyncio.get_event_loop().create_future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())