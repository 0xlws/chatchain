from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()


def get_env_var(key, default=None):
    return os.environ.get(key, default)


# Twitter
ACCESS_TOKEN = get_env_var("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = get_env_var("ACCESS_TOKEN_SECRET")
API_KEY = get_env_var("API_KEY")
API_SECRET_KEY = get_env_var("API_SECRET_KEY")
BEARER_TOKEN = get_env_var("BEARER_TOKEN")

# Discord
DISCORD_BOT_TOKEN = get_env_var("DISCORD_BOT_TOKEN")

# SD_AUTOMATIC1111
GRADIO_URL = "https://23a69d47-5e38-4ldf.gradio.live"

# OpenAI
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")

# Pinecone
# PINECONE_API_KEY    = get_env_var("PINECONE_API_KEY")
# PINECONE_ENVIRONMENT= get_env_var("PINECONE_ENVIRONMENT")
# PINECONE_INDEX      = get_env_var("PINECONE_INDEX")

# Dreamstudio
DREAMSTUDIO_API_KEY = get_env_var("DREAMSTUDIO_API_KEY")

# Telegram
TELEGRAM_BOT_TOKEN = get_env_var("TELEGRAM_BOT_TOKEN")
TELEGRAM_OWNER_ID = get_env_var("TELEGRAM_OWNER_ID")
