import PyPDF2
import requests
import io
from discord_bot.utils.setup_handler import SetupHandler


class FileReaderPlugin(SetupHandler):
    def setup(bot):
        @bot.command(name="process_pdf")
        async def process_pdf(ctx, url: str = None):
            if not any(
                [a.url.lower().endswith(".pdf") for a in ctx.message.attachments]
            ) and not (url and url.lower().endswith(".pdf")):
                await ctx.send("Please provide a valid PDF file.")
                return

            pdf_content = []

            if url and url.lower().endswith(".pdf"):
                response = requests.get(url)
                with io.BytesIO(response.content) as open_pdf_file:
                    read_pdf(open_pdf_file, pdf_content)
            elif any([a.url.lower().endswith(".pdf") for a in ctx.message.attachments]):
                pdf_url = next(
                    a.url
                    for a in ctx.message.attachments
                    if a.url.lower().endswith(".pdf")
                )
                response = requests.get(pdf_url)
                with io.BytesIO(response.content) as open_pdf_file:
                    read_pdf(open_pdf_file, pdf_content)

            # Do something with pdf_content, e.g. similarity search and store overlapping pieces
            await ctx.send("PDF is processed and ready!")

        def read_pdf(pdf_file, pdf_content):
            try:
                # Read the PDF file
                pdf_reader = PyPDF2.PdfReader(pdf_file)

                # Extract text and split into paragraphs
                for page_num in range(len(pdf_reader.pages)):
                    text = pdf_reader.pages[page_num].extract_text()
                    paragraphs = text.split("\n\n")
                    pdf_content.extend(paragraphs)
            except Exception as e:
                print(f"Error reading PDF file: {e}")
