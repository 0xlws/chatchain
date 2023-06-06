import re
from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        if transcript:
            text = ""
            for entry in transcript:
                rounded_start_time = int(entry["start"])
                text += f"{rounded_start_time}: {entry['text']}\n"
            return text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def filter_timestamps(timestamps, window=10):
    sorted_timestamps = sorted(timestamps)
    filtered_timestamps = [
        t
        for i, t in enumerate(sorted_timestamps)
        if i == 0 or t - sorted_timestamps[i - 1] >= window
    ]
    return filtered_timestamps


def generate_shortened_time_urls(original_url, timestamps):
    video_id_match = re.search(r"v=([a-zA-Z0-9-_]+)", original_url)
    if video_id_match:
        video_id = video_id_match.group(1)
        result_urls = [
            f"https://youtu.be/{video_id}?t={time_arg}" for time_arg in timestamps
        ]
    else:
        result_urls = [original_url] * len(timestamps)
    return result_urls


async def attempt_gpt_3(text, query, retries, ctx):
    for i in range(retries):
        try:
            response = await gpt_3(text, query)

            print("Response: ", response)
            timestamps = [
                int(t.strip()) for t in response.split(",") if t.strip().isdigit()
            ]
            return timestamps
        except:
            return []


async def gpt_3(text, query):
    prompt = f"Transcript:\n{text}\n\nIn the provided video transcript, provide the timestamps (in seconds) for the following query: {query}\n\nTimestamps (Only respond with a list of numbers if found, separated by commas): "
    answer = await assistant.ask(
        prompt, temperature=0.5, max_tokens=100, model="gpt-3.5-turbo"
    )
    return answer


def parse_video_id(url):
    matches = re.search(
        r"((?<=(v|V)/)|(?<=be/)|(?<=(\?|\&)v=)|(?<=embed/))([\w-]+)", url
    )
    video_id = matches.group() if matches else None
    return video_id


async def get_answer(url, query, ctx):
    video_id = parse_video_id(url)
    transcript = get_transcript(video_id)

    if transcript:
        transcript = transcript[:8000] + "..."
        timestamps = await attempt_gpt_3(transcript, query, 3, ctx)
    else:
        timestamps = []

    if timestamps:
        filtered_timestamps = filter_timestamps(timestamps)
        result_urls = generate_shortened_time_urls(url, filtered_timestamps)

        result_lines = [
            f"**{query} mention {i + 1}/{len(result_urls)}**: {result_url}"
            for i, result_url in enumerate(result_urls)
        ]
        result_msg = "\n".join(result_lines)
        return result_msg
    else:
        return "Not found."
