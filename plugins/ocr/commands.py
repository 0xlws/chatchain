import os
from discord_bot.utils.setup_handler import SetupHandler
from plugins.ocr.ocr import ocr_fn


class OCRCommands(SetupHandler):
    def setup(self):
        @self.assistant.command(name="ocr")
        async def ocr_command(ctx):
            if not ctx.message.attachments:
                await ctx.send("Please attach an image to perform OCR on.")
                return

            attachment = ctx.message.attachments[0]
            image_path = f"./{attachment.filename}"
            await attachment.save(image_path)

            try:
                extracted_text = ocr_fn(image_path)
                os.remove(image_path)

                await ctx.send(f"Text extracted with OCR:\n{extracted_text}")
            except Exception as e:
                print(f"Error during OCR: {e}")
                await ctx.send("Error during OCR, please try again.")
