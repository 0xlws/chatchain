from io import BytesIO
import PyPDF2


async def read_pdf(attachment):
    content = ""
    file_content = await attachment.read()

    with BytesIO(file_content) as file_stream:
        reader = PyPDF2.PdfReader(file_stream)
        for page_number in range(len(reader.pages)):
            content += reader.pages[page_number].extract_text()

    return content
