import json
import os
import pathlib
from discord_bot.utils.setup_handler import SetupHandler
from llm.openai.gpt_api import calculate_usage
import discord
import importlib.util
from pathlib import Path


def setup(bot):
    for period in ["hourly", "daily", "weekly", "monthly", "yearly"]:
        calculate_usage(period)


def create_usage_embed():
    from llm.openai.gpt_api import usage_file_path

    # Read current usage data
    with open(usage_file_path, "r") as usage_file:
        usage_data = json.load(usage_file)

    # Create an embed object
    embed = discord.Embed(
        title="Token Usage Statistics",
        description="Here's the token usage for different time periods:",
        color=discord.Color.blue(),
    )

    # Add usage data to the embed object
    for period in ["hourly", "daily", "weekly", "monthly", "yearly"]:
        period_stats = sorted(
            usage_data[period].items(), key=lambda x: x[1]["timestamp"]
        )
        usage_info = ""

        for key, stat in period_stats:
            if len(usage_info) + len(f"{key}: {stat['total_tokens']} tokens\n") <= 1024:
                usage_info += f"{key}: {stat['total_tokens']} tokens\n"
            else:
                break

        if not usage_info:
            usage_info = "No usage data available."

        embed.add_field(
            name=f"{period.capitalize()} usage", value=usage_info, inline=False
        )

    return embed


def load_handlers(bot):
    handlers_folders = [
        pathlib.Path(os.path.abspath("discord_bot/")),
        pathlib.Path(os.path.abspath("plugins/")),
        pathlib.Path(os.path.abspath("llm/")),
    ]

    ignore_folders = ["venv", "output", "__pycache__"]

    target_files = ["commands.py", "discord_interface.py"]

    for folder in handlers_folders:
        folder = Path(folder).resolve()
        print(f"Searching for files in: {folder}")

        for item in folder.rglob("*.py"):
            if any(ignore_folder in item.parts for ignore_folder in ignore_folders):
                continue

            # Check if the found file is one of the target files
            if item.name not in target_files:
                continue

            module_name = item.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, item)
                if spec is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in module.__dict__.items():
                        if (
                            isinstance(obj, type)
                            and issubclass(obj, SetupHandler)
                            and obj != SetupHandler
                        ):
                            obj(bot)

                    print(f"+ Successfully loaded: {item}")
                else:
                    pass
            except Exception as ex:
                print(f"- Failed to load module '{item}'. Reason: {ex}")
