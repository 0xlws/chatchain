import json
from typing import List
import discord
from interfaces.discord_bot.utils.setup_handler import SetupHandler
from plugins.config.config_env import OPENAI_API_KEY


user_config = {
    "model": "gpt4",
    "prompt": "",
    "context": "",
    "temperature": 1.0,
    "max_tokens": 100,
    "n": 1,
}


class LLMCommands(SetupHandler):
    def setup(self):
        if not OPENAI_API_KEY:
            return

        @self.assistant.tree.command(name="preferences")
        async def prefs(
            ctx,
            assistant_enabled: bool,
            only_owner: bool,
            response_locations: str,
            response_type: str = "mention",
            auto_thread_creation: bool = True,
            format_response: bool = False,
            thinking_message: bool = True,
            ephemeral: bool = True,
        ):
            # Update the relevant settings for the user
            self.assistant_enabled = assistant_enabled
            self.response_locations = (
                response_locations
                if response_locations in ["any", "only_threads", "only_channels"]
                else "any"
            )
            self.only_owner = only_owner
            self.auto_thread_creation = auto_thread_creation
            self.response_type = (
                response_type
                if response_type in ["reply/mention", "message"]
                else "reply/mention"
            )
            self.thinking_message = thinking_message
            self.format_response = format_response
            self.ephemeral = ephemeral

            # Send a confirmation message with the updated settings
            await ctx.response.send_message(
                f"Settings updated for user {ctx.user.mention}:\n"
                f"```{json.dumps(self.get_all_settings(), indent=4)}```",
                ephemeral=self.ephemeral,
            )

        @prefs.autocomplete("response_locations")
        async def config_locations_auto(
            interaction: discord.Interaction,
            current: str,
        ) -> List[discord.app_commands.Choice[str]]:
            choices = ["any", "only_threads", "only_channels"]
            return [
                discord.app_commands.Choice(name=choice, value=choice)
                for choice in choices
                if current.lower() in choice.lower()
            ]

        @prefs.autocomplete("response_type")
        async def config_message_type_auto(
            interaction: discord.Interaction,
            current: str,
        ) -> List[discord.app_commands.Choice[str]]:
            choices = ["reply/mention", "message"]
            return [
                discord.app_commands.Choice(name=choice, value=choice)
                for choice in choices
                if current.lower() in choice.lower()
            ]
