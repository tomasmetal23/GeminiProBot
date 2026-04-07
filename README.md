<h1 align="center">GemmaProBot 🤖✨</h1>

<p align="center">
  <em>Telegram bot powered by a local Gemma model via LM Studio — no cloud, no Google API key, fully private.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/branch-gemma-blueviolet?style=flat-square" />
  <img src="https://img.shields.io/badge/python-3.11-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/framework-Pyrogram%20async-green?style=flat-square" />
  <img src="https://img.shields.io/badge/model-Gemma%204%2026B-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/search-DuckDuckGo-red?style=flat-square" />
</p>

---

## 🌟 Features

| Feature | Comando | Descripción |
|---|---|---|
| 💬 Chat con memoria | `/gem <prompt>` | Conversa con Gemma. Recuerda el hilo completo de la conversación |
| 🌐 Búsqueda web | `/web <query>` | Busca en DuckDuckGo e inyecta los resultados como contexto para una respuesta actualizada |
| 🖼️ Análisis de imagen | `/img` _(reply a foto)_ | Describe o analiza una imagen usando el modelo Vision |
| 📄 Análisis de documentos | `/doc` _(reply a PDF/TXT)_ | Extrae el texto y pide a Gemma que lo resuma o analice |
| 🧠 System prompt propio | `/system <prompt>` | Define la personalidad del bot para tu usuario |
| 🗑️ Reset de memoria | `/reset` | Borra tu historial de conversación y empieza desde cero |
| 📡 Estado del servidor | `/status` | Comprueba si LM Studio está online, latencia y modelos disponibles |
| 🔒 Whitelist de usuarios | `.env` | Restringe el bot a una lista de IDs de Telegram |

---

## 🏗️ Arquitectura

```
GemmiProBot
├── src/
│   ├── gemini.py       ← Bot principal (async, todos los handlers)
│   ├── memory.py       ← Memoria persistente en SQLite por usuario
│   ├── search.py       ← Búsqueda web via DuckDuckGo (sin API key)
│   ├── config.py       ← Variables de entorno y whitelist
│   └── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example        ← Plantilla de configuración
└── data/               ← Volumen Docker: aquí vive bot_memory.db
```

El bot corre **100% local**:
- **LM Studio** sirve el modelo Gemma 4 26B en tu PC con la 7900 XT
- **Tailscale** conecta el servidor VPS con tu máquina local via IP privada
- **Pyrogram async** maneja toda la comunicación con Telegram en modo asíncrono

---

## ⚙️ Requisitos

- Docker y docker-compose instalados en el servidor
- [LM Studio](https://lmstudio.ai/) corriendo en tu PC local con el servidor local activo
- El modelo `gemma-4-26b-a4b-it-uncensored` (o cualquier compatible) cargado en LM Studio
- Conexión Tailscale entre el VPS y tu PC local
- Credenciales de Telegram: API ID, API Hash y Bot Token

---

## 🚀 Deploy con Docker (recomendado)

### 1. Clona el repo y cambia a la rama gemma

```bash
git clone https://github.com/tomasmetal23/GeminiProBot.git
cd GeminiProBot
git checkout gemma
```

### 2. Configura el entorno

```bash
cp .env.example .env
nano .env   # Rellena con tus datos reales
```

### 3. Levanta el bot

```bash
docker compose up -d
```

La imagen se descarga automáticamente desde el registro — no necesitas buildear nada localmente.

```bash
# Ver logs en tiempo real
docker compose logs -f

# Detener
docker compose down
```

---

## 🛠️ Variables de entorno

| Variable | Obligatoria | Descripción |
|---|---|---|
| `API_ID` | ✅ | Tu Telegram API ID ([my.telegram.org](https://my.telegram.org)) |
| `API_HASH` | ✅ | Tu Telegram API Hash |
| `BOT_TOKEN` | ✅ | Token de [@BotFather](https://t.me/BotFather) |
| `LM_STUDIO_URL` | ✅ | URL de LM Studio, ej: `http://100.x.x.x:11434/v1` |
| `MODEL_NAME` | ✅ | Nombre del modelo cargado en LM Studio |
| `ALLOWED_USERS` | ❌ | IDs de Telegram separados por coma. Vacío = abierto a todos |
| `MAX_HISTORY` | ❌ | Mensajes máximos recordados por usuario (default: `20`) |
| `DEFAULT_SYSTEM_PROMPT` | ❌ | Prompt de sistema por defecto del modelo |

---

## 📖 Guía de uso

### 💬 `/gem` — Chat con memoria

Conversa con Gemma. El bot recuerda toda la conversación (hasta `MAX_HISTORY` mensajes), así puedes hacer seguimiento sin repetir contexto.

```
/gem ¿Qué es la termodinámica?
/gem ¿Y cuáles son sus leyes?     ← recuerda la pregunta anterior
/gem Ponme un ejemplo con café     ← sigue el hilo
```

---

### 🌐 `/web` — Búsqueda web + respuesta de Gemma

Cuando necesites información actual que el modelo no tiene (precios, noticias, eventos recientes), usa `/web`. El bot busca en DuckDuckGo, inyecta los resultados como contexto y Gemma responde con datos frescos.

```
/web precio del bitcoin hoy
/web últimas noticias sobre IA en 2025
/web mejores GPUs para LLMs locales
```

> 💡 **Truco**: Si `/gem` no te da una respuesta suficientemente actualizada, repite la pregunta con `/web`.

---

### 🖼️ `/img` — Análisis de imagen

Envía una imagen al chat, respóndele con el comando `/img` y un prompt opcional. Requiere un modelo con capacidad Vision cargado en LM Studio.

```
1. Envía una foto
2. Responde a esa foto con:
   /img ¿Qué hay en esta imagen?
   (o sin prompt para descripción automática)
```

> ⚠️ **IMPORTANTE SOBRE MODELOS VISION:**  
> Modelos estándar como **Gemma 4, Llama 3 o Mistral son exclusivamente de texto**. Si les pasas una imagen a través del comando `/img`, LM Studio devolverá un error 400 (`Model does not support images`). Para poder usar el comando `/img` necesitas cargar un modelo **multimodal (Vision)** en LM Studio, como por ejemplo *Qwen-VL-Chat*, *Llava* o *Moondream*.


---

### 📄 `/doc` — Análisis de documentos

Funciona igual que `/img` pero con archivos PDF, TXT o Markdown.

```
1. Envía un archivo PDF o TXT
2. Responde a ese archivo con:
   /doc Resume los puntos clave
   /doc ¿Cuál es la conclusión principal?
```

---

### 🧠 `/system` — System prompt personalizado

Define la personalidad del bot solo para ti. Se guarda en la base de datos y persiste aunque reinicies el container.

```
/system Eres un experto en ciberseguridad que responde de forma técnica y precisa.
/system Eres un asistente de cocina que solo habla de recetas mediterráneas.
/system reset    ← vuelve al prompt por defecto
/system          ← muestra el prompt actual
```

---

### 🗑️ `/reset` — Borrar historial

Elimina toda tu conversación guardada. Útil para cambiar de tema o si el contexto se volvió confuso.

```
/reset
```

---

### 📡 `/status` — Estado del servidor

Comprueba en tiempo real si LM Studio está respondiendo, cuánto tarda y qué modelos tiene disponibles.

```
/status
```

Respuesta de ejemplo:
```
✅ LM Studio conectado (142ms)

Servidor: http://100.x.x.x:11434/v1
Modelo activo: gemma-4-26b-a4b-it-uncensored

Modelos disponibles:
  • gemma-4-26b-a4b-it-uncensored
```

---

## 🔒 Whitelist (acceso restringido)

Para que solo ciertos usuarios puedan usar el bot, añade sus IDs en el `.env`:

```env
ALLOWED_USERS=123456789,987654321
```

Para obtener tu ID de Telegram habla con [@userinfobot](https://t.me/userinfobot).

Si `ALLOWED_USERS` está vacío, cualquier persona puede usar el bot.

---

## 🔄 CI/CD — GitHub Actions

El workflow `.github/workflows/docker.yml` buildea y pushea la imagen automáticamente a `ghcr.io` cuando haces push a `main` o `gemma` con cambios en `src/` o `Dockerfile`.

Imagen resultante: `ghcr.io/tomasmetal23/gemmaprobot:latest`

---

## Maintainer 🚀

- **Tomás Márquez**
  - Telegram: [@natebrako](https://t.me/natebrako)

> *Rama `gemma`: versión local-first del bot, sin dependencia de APIs de Google. El modelo corre en tu propia GPU.*
