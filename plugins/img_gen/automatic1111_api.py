import json
import requests
import base64
from PIL import Image
from io import BytesIO
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = "output"
image_output_dir = os.path.join(script_dir, folder_name)


class TextToImage:
    def __init__(self, url):
        self.gradio_url = url
        self.set_default_values()

    def set_url(self, url):
        self.gradio_url = url

    def set_default_values(self):
        self.simple_txt2img = {
            "enable_hr": False,
            "hr_scale": 0,
            "hr_upscaler": "ESRGAN_4x",
            "hr_second_pass_steps": 0,
            "denoising_strength": 0,
            "firstphase_width": 0,
            "firstphase_height": 0,
            "prompt": "example prompt",
            "styles": [],
            "seed": -1,
            "subseed": -1,
            "subseed_strength": 0,
            "seed_resize_from_h": -1,
            "seed_resize_from_w": -1,
            "batch_size": 1,
            "n_iter": 1,
            "steps": 10,
            "cfg_scale": 7,
            "width": 64,
            "height": 64,
            "restore_faces": False,
            "tiling": False,
            "negative_prompt": "(sexy, nsfw, nude, naked: 2.0), (deformed, distorted, disfigured: 1.3),3d, cartoon, anime, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers: 1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation",
            "eta": 0,
            "s_churn": 0,
            "s_tmax": 0,
            "s_tmin": 0,
            "s_noise": 1,
            "sampler_index": "DPM++ SDE Karras",
        }

    async def create_image(
        self,
        prompt,
        steps=40,
        width=64,
        height=64,
        enable_hr=False,
        wide=False,
        seed=-1,
        tiling=False,
        negative_prompt="",
        n_iter=1,
    ):
        self.set_image_attributes(
            "((best quality)), ((masterpiece)), (detailed), " + prompt,
            steps,
            width,
            height,
            enable_hr,
            wide,
            seed,
            tiling,
            negative_prompt,
            n_iter,
        )
        response = self.send_request()

        if response.status_code == 200:
            return self.process_successful_response(response)
        elif response.status_code == 422:
            return self.process_unprocessable_response(response)
        else:
            raise Exception(f"Failed to generate image, status code: {response}")

    def set_image_attributes(
        self,
        prompt,
        steps,
        width,
        height,
        enable_hr,
        wide,
        seed,
        tiling,
        negative_prompt,
        n_iter,
    ):
        self.simple_txt2img.update(
            {
                "prompt": prompt,
                "steps": steps,
                "width": width,
                "height": height,
                "enable_hr": enable_hr,
                "tiling": tiling,
                "hr_scale": 1.5 if wide else 2.5,
                "hr_upscaler": "ESRGAN_4x",
                "hr_second_pass_steps": 0,
                "denoising_strength": 0.25 if wide else 0.25,
                "firstphase_width": 911 if wide else 512,
                "firstphase_height": 512 if wide else 512,
                "n_iter": n_iter,
                "seed": seed,
                "negative_prompt": "(sexy, nsfw, nude, naked: 2.0), (deformed, distorted, disfigured: 1.3),3d, cartoon, anime, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, poorly drawn, bad anatomy, wrong anatomy, extra limb, missing limb, floating limbs, (mutated hands and fingers: 1.4), disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation"
                if not negative_prompt
                else negative_prompt,
            }
        )

    def send_request(self):
        return requests.post(
            f"{self.gradio_url}/sdapi/v1/txt2img", json=self.simple_txt2img, timeout=300
        )

    def process_successful_response(self, response):
        try:
            images, parameters, info = (
                response.json()["images"],
                response.json()["parameters"],
                response.json()["info"],
            )

            b64_image = images[0]
            img_data = base64.b64decode(b64_image)
            return img_data, parameters, info
        except ValueError:
            raise Exception("Failed to parse response JSON")

    def process_unprocessable_response(self, response):
        try:
            error = response.json()
            return None, None, error["detail"]
        except ValueError:
            raise Exception("Failed to parse response JSON")


def save_image(image_bytes, info):
    """returns: image_path, image_filename"""

    image_files_list = os.listdir(image_output_dir)
    image_nr = len([file for file in image_files_list if file.endswith(".png")])

    image = Image.open(BytesIO(image_bytes))
    image_filename = f"{image_nr}_{json.loads(info)['seed']}.png"
    image_path = os.path.join(image_output_dir, image_filename)
    image.save(image_path)
    return image_path, image_filename
