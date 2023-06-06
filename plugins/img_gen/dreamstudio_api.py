import base64
import requests
import json
from plugins.config.config_env import DREAMSTUDIO_API_KEY

api_key = DREAMSTUDIO_API_KEY

if api_key is None:
    raise Exception("Missing Stability API key.")


api_host = "https://api.stability.ai"


def get_engines():
    url = f"{api_host}/v1/engines/list"

    response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    # Do something with the payload...
    payload = response.json()
    return payload


print(json.dumps(get_engines(), indent=4))


def generate_image(prompt: str, engine_id="stable-diffusion-v1.5"):
    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 512,
            "width": 512,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.ok:
        response_data = response.json()
        data = response_data["artifacts"][0]
        if data["finishReason"] == "SUCCESS":
            return base64.b64decode(data["base64"])
    else:
        raise Exception("Error generating image: %s", response.text)
