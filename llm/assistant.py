from discord_bot.utils.setup_handler import SetupHandler

from llm.interfaces.text_cli import GPTCLI
from llm.interfaces.discord_interface import DiscordHandler, UserSettings
from llm.utils.utils import sanitize_output

from .openai.gpt_api import async_generate_chat_completion


class AIAssistant(DiscordHandler, UserSettings, GPTCLI, SetupHandler):
    def __init__(self, command_prefix=None, intents=None):
        if command_prefix and intents:
            DiscordHandler.__init__(
                self, command_prefix=command_prefix, intents=intents
            )
            SetupHandler.__init__(self, self)
            UserSettings.__init__(self, self.owner_id)

        self.model = "gpt-4"
        self.temperature = 1
        self.max_tokens = None
        self.n = 1
        # self.top_p = 1
        # self.stream = False
        # self.stop = None
        # self.presence_penalty = 0
        # self.frequency_penalty = 0
        # self.logit_bias = None
        # self.user = None

    async def response(self, input, **kwargs):
        return await self.code(input, **kwargs)

    async def _generate_text(self, prompt, system_role="", max_tokens=None, **kwargs):
        if not prompt:
            return ""

        try:
            return await async_generate_chat_completion(
                prompt, max_tokens=max_tokens or 4000, system_role=system_role, **kwargs
            )
        except Exception as e:
            print(f"Error generating text for prompt '{prompt}': {e}")
            return ""

    async def generate_description(self, content, max_tokens=25):
        prompt = f"```\n{content}\n```\n\nPlease describe in 10 words or less the user's message. Your output will be directly used for the name of the thread.\nDescription:\n"
        return sanitize_output(
            await self._generate_text(
                prompt=prompt, system_role="", max_tokens=max_tokens
            )
        )

    async def code(
        self,
        prompt="",
        system_role="""You are senior dev text and code generation AI assistant.""",
        **kwargs,
    ):
        if not prompt:
            return
        try:
            return await async_generate_chat_completion(
                prompt=prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                model=self.model,
                system_role=system_role,
                n=self.n,
                **kwargs,
            )
        except Exception as e:
            print(e)
            return ""


assistant = AIAssistant()
