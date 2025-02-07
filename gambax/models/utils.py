
from gambax.models.chatgpt import ChatGPT
from gambax.models.huggingface import HuggingfaceLLM
from gambax.utils.plugin import instantiate_from_config

def load_model(model_name: str, custom_models:dict = {}):

    model = None
    if model_name.lower().startswith("gpt"):
        model = ChatGPT(model_name=model_name)
    elif model_name in custom_models:
        try:
            model = instantiate_from_config(custom_models[model_name])
        except Exception as e:
            print(f"Error loading custom model '{model_name}': {str(e)}")
            return None
    else:
        try:
            model = HuggingfaceLLM(model_name=model_name)
        except Exception as e:
            print(f"Error loading HuggingFace model '{model_name}': {str(e)}")
    
    return model