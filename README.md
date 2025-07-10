# README.md

<h1 align="center">Gemini Pro Telegram Bot 🌌</h1>

<p align="center">
  <em>Gemini Pro: An AI-powered Telegram bot script for generating text and image-based responses using Gemini AI</em>
</p>
<hr>

## 🌟 Features

- 🍪 **Text Prompt Response**: Accepts text prompts and generates text.
- 🖼️ **Image Recognition**: Can read and interpret images.

## Requirements

Before you begin, ensure you have met the following requirements for a local setup:

-   Python 3.9 or higher.
-   All Python libraries listed in the `src/requirements.txt` file. The main libraries are `pyrogram`, `google-generativeai`, and `pillow`.
-   A Telegram bot token (you can get one from [@BotFather](https://t.me/BotFather) on Telegram).
-   A Telegram API ID and API Hash (you can get these from [my.telegram.org](https://my.telegram.org)).
-   A Google Generative AI API Key (you can get one from [Google AI Studio](https://makersuite.google.com/app/apikey)).

## Installation

To install all the required libraries at once, navigate to the project's root directory and run the following command. It is highly recommended to do this inside a virtual environment.

```bash
pip install -r src/requirements.txt
```
## Configuration

1. Open the `config.py` file in your favorite text editor.
2. Replace the placeholders for `API_ID`, `API_HASH`, `GOOGLE_API_KEY`, and `BOT_TOKEN` with your actual values:
   - **`API_ID`**: Your API ID from [my.telegram.org](https://my.telegram.org).
   - **`API_HASH`**: Your API Hash from [my.telegram.org](https://my.telegram.org).
   - **`GOOGLE_API_KEY`**: To get google api key [Click Here](https://makersuite.google.com/app/apikey).
   - **`BOT_TOKEN`**: The token you obtained from [@BotFather](https://t.me/BotFather).

## Deploy the Bot

```sh
git clone https://github.com/tomasmetal23/GeminiProBot.git
cd GeminiProBot
pip install -r src/requirements.txt
python src/gemini.py
```

## 🚀 Deploy with Docker

You can easily run this bot in a container using Docker and docker-compose.

### 1. Build and Run with Docker Compose

First, make sure you have Docker and docker-compose installed.

Clone the repository and move into the project directory:

```sh
git clone https://github.com/bisnuray/GeminiProBot
cd GeminiProBot
```

Edit the `docker-compose.yml` file and add your API credentials in the `environment` section:

```yaml
version: "3.8"
services:
  gemini_bot:
    image: ghcr.io/tomasmetal23/geminiprobot:latest
    environment:
      - API_ID=your_api_id
      - API_HASH=your_api_hash
      - BOT_TOKEN=your_bot_token
      - GOOGLE_API_KEY=your_google_api_key
      - MODEL_NAME=gemini-2.5-pro  # You can use any supported Gemini model
    restart: unless-stopped
```

Replace the values with your actual API keys and tokens.  
You can use any supported Gemini model for `MODEL_NAME` (e.g., `gemini-1.5-flash`, `gemini-2.0-flash`, `gemini-2.5-pro`).

### 2. Start the Bot

```sh
docker-compose up -d
```

The bot will start automatically and use the environment variables you provided in `docker-compose.yml`.

---

## 🛠️ Environment Variables

- `API_ID`: Your Telegram API ID.
- `API_HASH`: Your Telegram API Hash.
- `BOT_TOKEN`: The token from [@BotFather](https://t.me/BotFather).
- `GOOGLE_API_KEY`: Your Google Generative AI API key.
- `MODEL_NAME`: (Optional) Gemini model name, default is `gemini-1.5-flash`. You can use newer models like `gemini-2.0-flash` or `gemini-2.5-pro` if your API key supports them.

---

Now you can manage your bot easily with Docker!

## How to Use the Bot 🛠️

This bot offers two main features: text generation and image analysis.

### 📝 Text Generation

To generate a text response, use the `/gem` command followed by your question or instruction.

**Example:**
> `/gem Write a short poem about space.`

### 🖼️ Image Analysis

To ask the bot about an image, follow these steps:

1.  Send an image to the chat.
2.  Reply directly to that image using the `/imgai` or `/img` command.

## Author 📝

- Name: Bisnu Ray
- Telegram: [@SmartBisnuBio](https://t.me/SmartBisnuBio)

## Maintainer & Latest Update 🚀

- **Updated & Maintained by**: Tomás Márquez
  - Telegram: [@natebrako](https://t.me/natebrako)
  - *Current Status: Updated to 2025 and ongoing maintenance.*
  
Feel free to reach out if you have any questions or feedback.
