from typing import Literal
import numpy as np
from openai import OpenAI
import logging
logger = logging.getLogger("gambax")

from gambax.services import Service


class ImageGenerationService(Service):
    name = "image_generation"

    def __init__(self, model_name: Literal["dall-e-3", "dall-e-2"] = "dall-e-3"):
        super().__init__(self.name, input_signature=["prompt", "size", "quality"], output_signature=["image_url"])
        self.model_name = model_name
        self.client = OpenAI()

    def request_impl(self, prompt: str, size:Literal["256x256", "512x512", "1024x1024", "1024x1792", "1792x1024"], quality: Literal["hd",'standard']="hd") -> np.ndarray:
        logger.info(f"Generating image with prompt '{prompt}', size '{size}', quality '{quality}'")
        response = self.client.images.generate(
            model=self.model_name,
            prompt=prompt,
            size=size,
            quality=quality,
            n=1,
        )
        url = response.data[0].url
        return url
    
    def get_tool(self):
        return {
            "type": "function",
            "function": {
                "name": "image_generation",
                "description": "Generate an image using DALL-E model.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Descriptive prompt for the image."
                        },
                        "size": {
                            "tpye": "string",
                            "enum": ["1024x1024", "1024x1792", "1792x1024"],
                            "description": "Size of the generated image."
                        },
                        "quality": {
                            "type": "string",
                            "enum": ["hd", "standard"],
                            "description": "Quality of the generated image."
                        }
                    },
                    "required": ["prompt", "size"]
                }
            }
        }