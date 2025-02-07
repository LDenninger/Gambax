import torch
from transformers import pipeline
from typing import List, Dict
import logging
logger = logging.getLogger("gambax")

from gambax.models.ModelInterface import ModelInterface

def chat_format_to_text(chat: List[Dict[str, str]]) -> str:
    prompt = ""
    for msg in chat:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            prompt += f"### System:\n{content}\n"
        elif role == "user":
            prompt += f"### Instruction:\n{content}\n"
        elif role == "assistant":
            prompt += f"### Response:\n{content}\n"
    # End with a user instruction or question, so the model knows to continue
    return prompt

class HuggingfaceLLM(ModelInterface):

    def __init__(self, 
                 model_name: str,
                 temperature:float=0.1,
                 max_tokens: int=2000,
                 top_p: float=1.0,
                 device: str='cuda'
                 ):
        super().__init__(model_name)

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.pipeline = pipeline("text-generation", model=model_name, device=device)
        logger.info(f"Initialized HuggingfaceLLM with model '{model_name}'")

    @torch.no_grad()
    def call_impl(self, messages: Dict[str,str], **kwargs):
        response = self.pipeline(messages)
        logger.info(f"Generated response: {response}")
        return response