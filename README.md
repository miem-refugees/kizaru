# kizaru bot

A Telegram bot that finds similar "punches" (lines, lyrics, or phrases) in a vector database based on the user's message. The bot is designed to search through a collection of Kizaru's lyrics and return the most similar line to what the user sends, using modern NLP embeddings and a vector database.

---

## Features

- **Semantic Search:** Finds the most similar lyric to any user message using sentence embeddings.
- **Vector Database:** Uses Qdrant for fast similarity search.
- **Admin Controls:** Adjust search thresholds, rate limits, and bot toggles via Telegram commands.
- **Multilingual Support:** Uses a multilingual embedding model for robust search.

---

## How It Works

1. **User sends a message** to the bot in Telegram.
2. The bot encodes the message using a sentence transformer model.
3. The embedding is searched in a Qdrant vector database containing Kizaru's lyrics.
4. The bot replies with the most similar lyric and its source.

---

## Setup

### Prerequisites

- Python 3.13+
- Docker (optional, for containerized deployment)
- Access to a running Qdrant instance (local or cloud)
- Telegram Bot Token

### Environment Variables

Create a `.env` file in the project root with the following variables:

```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_if_needed
TELEGRAM_ADMIN_IDS=123456789 987654321  # space-separated Telegram user IDs for admin access
MIN_WORDS=5
RANDOM_TRESHOLD=5
RATELIMIT_SEC=30
```

### Local Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/kizaru.git
   cd kizaru
   ```

2. **Install dependencies:**
   ```sh
   pip install uv
   uv sync
   # or, using pyproject.toml:
   uv sync
   ```

3. **Run the bot:**
   ```sh
   uv run bot/main.py
   ```

### Docker

1. **Build and run with Docker Compose:**
   ```sh
   docker-compose up --build
   ```

   This will use the prebuilt image or build from the Dockerfile, and expects a `.env` file for configuration.

2. **Qdrant Setup:**
   - You can run Qdrant locally via Docker:
     ```sh
     docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant
     ```
   - Or use a managed Qdrant Cloud instance.

---

## Usage

- **/start** — Greet the user.
- **/id** — Get your Telegram user ID.
- **/settings** — Open the settings menu (admin only).
- **/setrandom N** — Set the random threshold (admin only).
- **/setratelimit N** — Set the rate limit in seconds (admin only).

**To search:**
Just send any message (with enough words) to the bot, and it will reply with the most similar lyric.

---

## Data Pipeline

The `pipeline/` directory contains scripts for parsing, preprocessing, chunking, embedding, and uploading lyrics data to Qdrant.
See the scripts in `pipeline/` for details on preparing and updating the vector database.

---

## Development

- Main bot logic: `bot/`
- Data pipeline: `pipeline/`
- Notebooks for data exploration: `notebooks/`
- Lyrics data: `data/`

---

## License

MIT License. See [LICENSE](LICENSE) for details.
