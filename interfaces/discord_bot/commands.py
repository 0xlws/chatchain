from interfaces.discord_bot.utils.utils import create_usage_embed
from interfaces.discord_bot.utils.setup_handler import SetupHandler
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "output/conversation_history"

folder_name = os.path.join(script_dir, folder_name)
if not os.path.exists(folder_name):
    os.makedirs(folder_name)


class MainCommands(SetupHandler):
    def setup(self):
        @self.assistant.tree.command(
            name="clear",
            description="Clear a specific number of messages in the channel",
        )
        async def clear(interaction, limit: int):
            await interaction.response.send_message(
                f"Last {limit} messages cleared!", ephemeral=True
            )
            await interaction.channel.purge(limit=limit)

        @self.assistant.command()
        async def usage(ctx):
            embed = create_usage_embed()
            return await ctx.send(embed=embed)
