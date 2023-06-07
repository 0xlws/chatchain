import discord
from discord.ext import commands
from llm.interfaces.utills import (
    create_discord_file,
    enforce_types,
    process_attachments,
)
from plugins.config.config_env import OPENAI_API_KEY


class UserSettings:
    def __init__(self, user_id):
        self.user_id = user_id
        self.assistant_enabled = True
        self.only_owner = False
        self.response_type = "reply/mention"
        self.response_locations = "any"
        self.auto_thread_creation = True
        self.format_response = None
        self.ephemeral = True

    def get_all_settings(self):
        settings = {
            "user_id": self.user_id,
            "assistant_enabled": self.assistant_enabled,
            "only_owner": self.only_owner,
            "response_type": self.response_type,
            "response_locations": self.response_locations,
            "auto_thread_creation": self.auto_thread_creation,
            "format_response": self.format_response,
            "ephemeral": self.ephemeral,
        }

        return settings


class DiscordHandler(commands.Bot):
    def __init__(self, command_prefix, intents):
        if command_prefix and intents:
            super().__init__(command_prefix=command_prefix, intents=intents)

    def is_owner(self, message):
        return message.author.id == self.user_id

    @enforce_types
    async def on_message(self, message):
        if not isinstance(message, discord.message.Message):
            return
        if message.author.bot or not self.assistant_enabled:
            return
        if not OPENAI_API_KEY:
            return await message.channel.send(
                "It seems like the 'OPENAI_API_KEY' has not been set. Please set the 'OPENAI_API_KEY' in your environment variables and restart the application."
            )
        if message.content.startswith("."):
            return
        if message.content.startswith(("!", "/")):
            return await self.process_commands(message)

        if self.only_owner and not self.is_owner(message):
            return

        if not self.is_valid_channel(message):
            return

        try:
            return await self.handle_regular_message(message)
        except:
            return await message.channel.send(
                "Oops! An unexpected error occurred on our end 🤔. We apologize for the inconvenience. Please try again."
            )

    async def on_ready(self):
        print(f"============================================")
        print(f"   Successfully logged in as {self.assistant.user.name}")
        print(f"             ID: {self.assistant.user.id}")
        print(f"============================================")
        app_info = await self.application_info()
        self.user_id = app_info.owner.id
        print(f"🚀 Bot is now ready to use!")
        print(f"👤 Owner ID: {self.user_id}")
        synced = await self.tree.sync()
        print(f"- Successfully synced {len(synced)} command(s) in the '/' directory.")

    def is_thread(self, user_message):
        return user_message.channel.type in (
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
        )

    @enforce_types
    async def send_response(
        self,
        message: discord.message.Message,
        content: str,
        description: str = "",
        reply_as_file: str = "",
        new_thread: discord.message.Message = None,
        mention: str = "",
    ):
        if new_thread:
            response_action = new_thread.send
            if reply_as_file:
                return await response_action(
                    content=f"{mention} {description}",
                    file=reply_as_file if reply_as_file else None,
                )
            else:
                return await response_action(content=f"{mention} {content}")
        else:
            response_action = message.reply

            if reply_as_file:
                return await response_action(
                    content=description, attachments=[reply_as_file]
                )
            else:
                return await response_action(content=content)

    async def handle_regular_message(self, message):
        await message.channel.typing()
        reply = await self.generate_reply(message)
        reply = reply[0]
        description, file = self.format_reply(reply)

        new_thread = None
        if not self.is_thread(message):
            new_thread = await self.create_thread(message, reply)

        return await self.send_response(
            message,
            reply,
            description=description,
            reply_as_file=file,
            new_thread=new_thread,
            mention=f"{message.author.mention}",
        )

    async def generate_reply(self, message):
        if message.attachments:
            return await self.process_attachment_message(message)
        if message.reference:
            return await self.process_reference_message(message)
        return await self.code(message.content)

    def format_reply(self, reply: str, description: str = ""):
        if len(reply) >= 2000:
            description = description if description else "Long message sent as a file:"
            file = create_discord_file(reply)
            return description, file
        else:
            return "", None

    def is_valid_channel(self, message):
        return (
            self.response_locations == "any"
            or (
                self.response_locations == "only_channels"
                and message.channel.type == discord.ChannelType.text
            )
            or (
                self.response_locations == "only_threads"
                and message.channel.type
                in (
                    discord.ChannelType.public_thread,
                    discord.ChannelType.private_thread,
                )
            )
        )

    async def process_attachment_message(self, user_message):
        content = (
            await process_attachments(user_message.attachments)
            if user_message.attachments
            else None
        )
        return await self.code(user_message.content, context=content)

    async def process_reference_message(self, user_message):
        replied_msg = await user_message.channel.fetch_message(
            user_message.reference.message_id
        )
        content = (
            await process_attachments(replied_msg.attachments)
            if replied_msg.attachments
            else None
        )
        prompt = (
            f"Assistant: {content}\nUser: {user_message.content}\nAssistant: "
            if content
            else f"Assistant: {replied_msg.content}\nUser: {user_message.content}\nAssistant: "
        )
        return await self.code(prompt)

    async def create_thread(self, user_message, reply):
        msg = user_message.content
        msg = " ".join(msg.split()[:20]) + "..." if len(msg.split()) > 20 else msg
        reply = (
            " ".join(reply.split()[:20]) + "..." if len(reply.split()) > 20 else reply
        )
        text = f"User: {msg}\nAssitant: {reply}\n"
        description = (await self.generate_description(text))[:100]
        result_thread = await user_message.channel.create_thread(
            name=description, message=user_message
        )
        return result_thread

    def get_response_type(self, user_message):
        if self.message_type == "mention/reply":
            return user_message.reply
        else:
            return user_message.channel.send
