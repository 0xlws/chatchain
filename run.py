from discord_bot.utils.utils import load_handlers
from llm.assistant import AIAssistant

assistant = AIAssistant()
load_handlers(assistant.discord_bot)

assistant.run()
