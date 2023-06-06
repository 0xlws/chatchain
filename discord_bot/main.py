import discord
from discord_bot.utils.utils import load_handlers
from llm.assistant import AIAssistant
import plugins.config.config_env as config_env



intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.messages = True
intents.guilds = True
intents.voice_states = True


assistant = AIAssistant(command_prefix="!", intents=intents)
load_handlers(assistant)



assistant.run(config_env.BOT_TOKEN)