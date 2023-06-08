import math


def chunk_text(text, max_len):
    text_len = len(text)

    if text_len <= max_len:
        return [text]

    num_chunks = math.ceil(text_len / max_len)
    return [text[i * max_len : (i + 1) * max_len] for i in range(num_chunks)]


def sanitize_output(text):
    if isinstance(text, list):
        text = text[0]
    return text.replace("'", "").replace('"', "")
