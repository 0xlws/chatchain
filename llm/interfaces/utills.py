import datetime
from io import BytesIO
import os
import tempfile

import discord
import requests

from plugins.formatting import format_response_py_v2
from plugins.reader import reader
from plugins.vector_store import chroma_manager
from functools import wraps
from typing import Callable, Any




def save_output_file(reply):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"output_{timestamp}.py"
    folder_path = "./llm/output"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filename = os.path.join(folder_path, output_filename)
    with open(filename, "w") as output_file:
        output_file.write(format_response_py_v2(reply))
    return reply


async def save_pdf_file(file_url, file_name, content, collection=None, db=None):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Download the file from the attachment or URL and save it to the temp file
        response = requests.get(file_url)
        temp_file.write(response.content)
        temp_file.close()  # Close the temp_file before using it for generating hash

        # Generate the file's hash
        sha256_hash = chroma_manager.ChromaManager().generate_file_hash(temp_file.name)
        # sha256_hash = chroma_manager.ChromaManager().generate_file_hash(content)

        # Check the database for duplicates and store the file if there's no duplicate
        if collection and database_contains_hash(sha256_hash, collection):
            # Save PDF file to the storage and metadata to the database
            db.chunk_upload(
                collection,
                content,
                metadatas={"sha256_hash": sha256_hash, "file_name": file_name},
            )  # extension

            # store_pdf_file(temp_file, sha256_hash, file_name)

        else:
            # await ctx.send(f"{file_name} already exists in the database.")
            pass


def database_contains_hash(file_hash, collection):
    # Check the database to see if the hash already exists
    # Return a boolean value
    if collection.get(where={"sha256_hash": file_hash}) == True:
        False
    True


def create_discord_file(content):
    file_extension = "txt"
    file_content = content.encode()
    file = discord.File(BytesIO(file_content), filename=f"content.{file_extension}")
    return file


def enforce_types(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        annotations = list(func.__annotations__.values())

        if hasattr(args[0], "__class__"):  # Check if there's a 'self' argument
            temp_args = args[1:]  # Remove the 'self' argument from the arguments list
        else:
            temp_args = args

        for arg, anno in zip(temp_args, annotations):
            if not isinstance(arg, anno):
                raise TypeError(
                    f"Expected argument of type {anno}, but got {type(arg)}"
                )
        return await func(*args, **kwargs)

    return wrapper


def format_reply(reply, description, user_message):
    if len(reply) >= 2000:
        # description = description if description else 'Long message sent as a file:'
        description = (
            description
            if description
            else f"{user_message.author.mention} Long message sent as a file:"
        )
        file = create_discord_file(reply)
        return description, file
    else:
        return reply, None

async def process_attachments(attachments, collection=None, db=None):
    content = ""
    for attachment in attachments:
        # Check if the file is a PDF file
        if attachment.filename.lower().endswith(".pdf"):
            if collection:
                content = await reader.read_pdf(attachment)
                # Extract text from the PDF file
                await save_pdf_file(
                    attachment.url,
                    attachment.filename,
                    content,
                    collection=collection,
                    db=db,
                )
                # await save_pdf_file(attachment.url, attachment.filename, collection=collection, db=db)
        else:
            file_content = (await attachment.read()).decode("utf-8")
            content += "\n\n___\n" + file_content

    return content
