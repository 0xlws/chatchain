import os
import openai
import json
import os
from datetime import datetime, timedelta
from plugins.config.config_env import OPENAI_API_KEY
import asyncio
import functools
import random


def store_json(json_obj):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folder_name = "output/response_history"

        folder_path = os.path.join(script_dir, folder_name)
        # Create folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        # Get the current timestamp and format it as a string
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{timestamp}.json"

        # Save the JSON object to a file in the specified folder
        with open(os.path.join(folder_path, file_name), "w") as json_file:
            json.dump(json_obj, json_file)
    except Exception as e:
        print(e)


# Check if usage folder exists, and create it if it doesn't
script_dir = os.path.dirname(os.path.abspath(__file__))
usage_folder = os.path.join(script_dir, "output/usage_data")
if not os.path.exists(usage_folder):
    os.makedirs(usage_folder)


# Check if usage.json exists, and create it if it doesn't
usage_file_path = os.path.join(usage_folder, "usage.json")
if not os.path.exists(usage_file_path):
    with open(usage_file_path, "w") as usage_file:
        json.dump(
            {"hourly": {}, "daily": {}, "weekly": {}, "monthly": {}, "yearly": {}},
            usage_file,
        )


def read_api_key(file_path):
    with open(file_path) as f:
        data = json.load(f)
        return data["OPENAI_API_KEY"]


openai.api_key = OPENAI_API_KEY


def set_openai_api_key(api_key):
    openai.api_key = api_key


def _create_embedding(text_list, model="text-embedding-ada-002"):
    return openai.Embedding.create(input=text_list, model=model)


def extract_embeddings(response):
    return [item["embedding"] for item in response["data"]]


def process_single_embedding(text):
    response = _create_embedding([text])
    return extract_embeddings(response)[0]


def process_multiple_embeddings(text_list):
    response = _create_embedding(text_list)
    return extract_embeddings(response)


def get_embeddings(text):
    if isinstance(text, list):
        return process_multiple_embeddings(text)
    return process_single_embedding(text)


def calculate_usage(usage_period):
    # Read current usage data
    with open(usage_file_path, "r") as usage_file:
        usage_data = json.load(usage_file)

    # Calculate usage for the specified period
    period_stats = sorted(
        usage_data[usage_period].items(), key=lambda x: x[1]["timestamp"]
    )

    print(f"{usage_period.capitalize()} usage:")
    for key, stat in period_stats:
        print(f"{key}: {stat['total_tokens']} tokens")


def update_usage_stats(usage):
    # Read current usage data
    with open(usage_file_path, "r") as usage_file:
        usage_data = json.load(usage_file)

    # Update usage data
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    hour_key = now.strftime("%Y-%m-%d %H")
    day_key = now.strftime("%Y-%m-%d")
    week_key = (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d")
    month_key = now.strftime("%Y-%m")
    year_key = now.strftime("%Y")

    for key, period in zip(
        [hour_key, day_key, week_key, month_key, year_key],
        ["hourly", "daily", "weekly", "monthly", "yearly"],
    ):
        if key not in usage_data[period]:
            usage_data[period][key] = {"timestamp": timestamp, "total_tokens": 0}

        usage_data[period][key]["timestamp"] = timestamp
        usage_data[period][key]["total_tokens"] += usage["total_tokens"]

    # Write updated usage data
    with open(usage_file_path, "w") as usage_file:
        json.dump(usage_data, usage_file)


def generate_completion(prompt, model="text-davinci-003", **kwargs):
    completion = openai.Completion.create(engine=model, prompt=prompt, **kwargs)
    return completion["choices"][0].text


def generate_chat_completion(
    messages,
    context="",
    system_role="You are a helpful assistant.",
    model="gpt-3.5-turbo",
    max_tokens=200,
    **kwargs,
):
    """
    Generates a chat completion using the OpenAI API.

    Args:
        messages (list or str): A list of message objects or a string prompt for the chat. Each message object has a 'role' (either 'system', 'user', or 'assistant') and 'content' (the message text).
        context (str, optional): Additional context to provide to the model in the form of text. Defaults to an empty string.
        system_role (str, optional): Initial instruction for the model's behavior. Defaults to 'You are a helpful assistant.'.
        model (str, optional): The name of the OpenAI model to use. Defaults to 'gpt-3.5-turbo'.
        **kwargs: Other keyword arguments to pass to the OpenAI ChatCompletion API.

    Returns:
        str: The generated chat completion as a single string.
    """

    if isinstance(messages, list):
        response = openai.ChatCompletion.create(
            model=model, messages=messages, max_tokens=max_tokens, **kwargs
        )
        return response["choices"][0]["message"]["content"]

    prompt_with_context = (
        f"```\n{context}\n```\n\nPrompt: {messages}\n\n" if context else messages
    )
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt_with_context},
    ]
    response = openai.ChatCompletion.create(
        model=model, messages=messages, max_tokens=max_tokens, **kwargs
    )
    return response["choices"][0]["message"]["content"]


def handle_response(response):
    choices = response["choices"]
    responses = []

    for choice in choices:
        responses.append(choice["message"]["content"])

    return responses

    """
    Generates a chat completion using the OpenAI API.

    Args:
        messages (list or str): A list of message objects or a string prompt for the chat. Each message object has a 'role' (either 'system', 'user', or 'assistant') and 'content' (the message text).
        context (str, optional): Additional context to provide to the model in the form of text. Defaults to an empty string.
        system_role (str, optional): Initial instruction for the model's behavior. Defaults to 'You are a helpful assistant.'.
        model (str, optional): The name of the OpenAI model to use. Defaults to 'gpt-3.5-turbo'.
        **kwargs: Other keyword arguments to pass to the OpenAI ChatCompletion API.

    Returns:
        str: The generated chat completion as a single string.
    """


def retry_async(num_retries, min_backoff, max_backoff):
    def decorator(f):
        async def wrapper(*args, **kwargs):
            for attempt in range(num_retries):
                try:
                    return await f(*args, **kwargs)
                except Exception as e:
                    backoff_duration = min_backoff * (2**attempt)
                    sleep_duration = backoff_duration + random.uniform(
                        0, max_backoff / 10
                    )
                    if attempt < num_retries - 1:
                        print(
                            f"Attempt {attempt + 1} failed. Retrying in {sleep_duration:.2f} seconds..."
                        )
                        await asyncio.sleep(sleep_duration)
                    else:
                        print(f"Attempt {attempt + 1} failed. Giving up.")
                        raise e

        return wrapper

    return decorator


@retry_async(3, 1, 16)
async def async_gpt_response(model, prompt, max_tokens, **kwargs):
    response = await asyncio.to_thread(
        functools.partial(
            openai.ChatCompletion.create,
            model=model,
            messages=prompt,
            max_tokens=max_tokens,
            **kwargs,
        )
    )

    response_data = {
        "request": {
            "prompt": prompt,
            "model": model,
            "max_tokens": max_tokens,
            **kwargs,
        },
        "response": response,
    }
    store_json(response_data)

    update_usage_stats(response["usage"])
    return handle_response(response)


async def async_generate_chat_completion(
    prompt,
    context="",
    system_role="You are a helpful assistant.",
    model="gpt-3.5-turbo",
    max_tokens=200,
    **kwargs,
):
    if isinstance(prompt, list):
        return await async_gpt_response(
            model=model, prompt=prompt, max_tokens=max_tokens, **kwargs
        )

    prompt_with_context = (
        f"```\n{context}\n```\n\nPrompt: {prompt}\n\n" if context else prompt
    )
    prompt = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt_with_context},
    ]

    return await async_gpt_response(
        model=model, prompt=prompt, max_tokens=max_tokens, **kwargs
    )


def transcribe_audio(file_path, model="whisper-1"):
    with open(file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(model, audio_file)
    return transcript


def generate_text_embedding(text):
    embedding = openai.Embedding.create(input=text, model="text-embedding-ada-002")

    vector = embedding["data"][0]["embedding"]
    return vector
