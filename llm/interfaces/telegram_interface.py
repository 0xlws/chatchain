import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
    CommandHandler,
)
from io import BytesIO
from telegram import InputFile
from plugins.config.config_env import TELEGRAM_BOT_TOKEN, TELEGRAM_OWNER_ID


async def keep_typing(context, chat_id):
    while True:
        await context.bot.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(7)


class TelegramHandler:
    def __init__(self, assistant):
        self.assistant = assistant
        self.application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        self.owner_id = TELEGRAM_OWNER_ID

    def set_owner(self, owner_id: int):
        self.owner_id = owner_id

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if not self.owner_id:
            self.set_owner(user_id)
            await update.message.reply_text("You are now set as the owner of this bot.")

        if str(user_id) != self.owner_id:
            print(f"Unauthorized access denied for {user_id}.")
            return

        # bot = update.effective_user
        # print(text="============================================")
        # print(text=f"   Successfully logged in as {bot.name}")
        # print(text=f"             ID: {bot.id}")
        print("============================================")
        print(f"🚀 Telegram bot is now ready to use!")
        print(f"👤 Telegram bot owner ID: {self.owner_id}")

    async def handle_msg(self, update, context, text=None):
        if not self.owner_id:
            return
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        message_id = update.effective_message.id
        text = text if text else update.effective_message.text

        if user_id != int(self.owner_id):
            print(f"Unauthorized access denied for {user_id}.")
            return

        if not text:
            return
        if update.message.reply_to_message:
            reply_to_text = update.message.reply_to_message.text
            text = f"Assistant: {reply_to_text}\nUser: {text}\nAssistant: "

        try:
            generate_reply_task = asyncio.create_task(self.assistant.code(text))
            typing_task = asyncio.create_task(keep_typing(context, chat_id))

            done, pending = await asyncio.wait(
                {generate_reply_task}, return_when=asyncio.FIRST_COMPLETED
            )

            typing_task.cancel()

            reply = generate_reply_task.result()
            reply = reply[0]

            if len(reply) > 4096:
                string_buffer = BytesIO(reply.encode())

                await update.message.reply_document(
                    document=InputFile(string_buffer, filename="long_text.txt"),
                    caption="Long message sent as a file:",
                )
            else:
                await update.message.reply_text(reply, reply_to_message_id=message_id)
        except Exception as e:
            print(e)
            typing_task.cancel()

    async def text_msg(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        return await self.handle_msg(
            update=update,
            context=context,
        )

    def setup_handlers(self):
        text_handler = MessageHandler(filters.TEXT, self.text_msg)
        start_handler = CommandHandler("start", self.start)

        self.application.add_handler(start_handler)
        self.application.add_handler(text_handler)

    def _run(self):
        self.setup_handlers()
        self.application.run_polling()
