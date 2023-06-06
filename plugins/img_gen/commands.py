import discord
from io import BytesIO
import requests
from PIL import Image
import requests
from discord_bot.utils.setup_handler import SetupHandler
from plugins.img_gen.automatic1111_api import TextToImage, save_image
from llm.openai.gpt_api import (
    _create_image,
)


text_to_image = TextToImage("")


class TextToImagePlugin(SetupHandler):
    def setup(self):
        @self.assistant.tree.command(name="set_gradio_url")
        async def set_gradio_url(interaction, url: str):
            text_to_image.set_url(url)

        @self.assistant.command(
            name="create", help="Create image from text description"
        )
        async def __create_image(ctx, *, prompt):
            img_url = _create_image(prompt)
            response = requests.get(img_url)
            image_data = BytesIO(response.content)

            await ctx.send(
                f"Generated image for {prompt}:",
                files=[discord.File(fp=image_data, filename="image.png")],
            )

        def get_engine_name(engine_id):
            for key, value in STABILITY_AI_CHOICES.items():
                if value == engine_id:
                    if "xl" in key:
                        return "XL-beta"
                    return key
            return "Unknown"

        STABILITY_AI_CHOICES = {
            "1": "stable-diffusion-v1",
            "1-5": "stable-diffusion-v1-5",
            "2": "stable-diffusion-512-v2-0",
            "2-768": "stable-diffusion-768-v2-0",
            "2-1": "stable-diffusion-512-v2-1",
            "2-1-768": "stable-diffusion-768-v2-1",
            "xl-beta": "stable-diffusion-xl-beta-v2-2-2",
        }

        @self.assistant.command()
        async def dreamai(ctx, engine_alias: str = None, *, prompt="_"):
            if engine_alias and prompt != "_":
                if engine_alias and engine_alias in STABILITY_AI_CHOICES:
                    engine_id = STABILITY_AI_CHOICES[engine_alias]
                else:
                    # Default choice if no alias provided or alias not found
                    engine_id = STABILITY_AI_CHOICES["1-5"]
                try:
                    negative_prompt = "| ugly :-1.0"
                    image_bytes = generate_image(
                        prompt + negative_prompt, engine_id=engine_id
                    )

                    if image_bytes:
                        image = Image.open(BytesIO(image_bytes))
                        image.save("result.png")

                        message = f"`{prompt}`"

                        await ctx.reply(message, file=discord.File("result.png"))

                    else:
                        await ctx.reply("Error: Image generation failed.")
                except Exception as e:
                    await ctx.reply(f"Error: {str(e)}")

            else:
                instruction = (
                    "To use the dream command, please provide a text prompt followed by an optional valid engine alias. For example:\n"
                    "`!dream 2 Beautiful landscape`\n\n"
                    "Available engine aliases are:"
                )
                alias_list = [
                    key for key in STABILITY_AI_CHOICES.keys() if "768" not in key
                ]
                alias_string = "\n".join(alias_list)
                await ctx.reply(f"{instruction}\n\n{alias_string}")

        @self.assistant.tree.command(
            name="generate_image", description="Generate image using AI"
        )
        async def texttoimage(
            interaction,
            prompt: str,
            n_iter: int = 1,
            steps: int = 40,
            # width: int = 512,
            # height: int = 512,
            # width: int = 64,
            # height: int = 64,
            # enable_hr: bool = False,
            # wide: bool = False,
            # seed: int = -1,
            # tiling: bool = False,
            negative_prompt: str = "(sexy, nsfw, nude, naked: 2.0), (deformed, distorted, disfigured: 1.3),3d, cartoon, anime, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers: 1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation",
        ):
            await interaction.response.defer()
            count = 0
            files = []

            for i in range(n_iter):
                image_bytes, parameters, info = await text_to_image.create_image(
                    prompt,
                    n_iter=1,
                    steps=steps,
                    negative_prompt=negative_prompt,
                    width=512,
                    height=512,
                )

                image_path, image_filename = save_image(image_bytes, info)
                files.append((image_path, image_filename))
                count += 1

                if (
                    count % 9 == 0 or count == n_iter
                ):  # Send a message every 9 images or at the end
                    message = await interaction.original_response()
                    if count == 1 and n_iter == 1:
                        await reply_to_message(
                            message,
                            prompt,
                            files[0][0],
                            files[0][1],
                            cmdtype="interaction",
                        )
                    else:
                        await reply_to_message2(
                            message, prompt, files[:9], cmdtype="interaction"
                        )
                        files = files[9:]

        async def reply_to_message(ctx, prompt, image_path, image_filename, cmdtype=""):
            if cmdtype == "interaction":
                return await ctx.edit(
                    content=f"`{prompt}`",
                    attachments=[discord.File(open(image_path, "rb"), image_filename)],
                )
            await ctx.reply(
                f"`{prompt}`",
                files=[discord.File(open(image_path, "rb"), image_filename)],
            )

        async def reply_to_message2(ctx, prompt, files, cmdtype=""):
            if cmdtype == "interaction":
                return await ctx.edit(
                    content=f"`{prompt}`",
                    attachments=[
                        discord.File(open(image_path, "rb"), image_filename)
                        for image_path, image_filename in files
                    ],
                )
