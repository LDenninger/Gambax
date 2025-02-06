
import json

from gambax.server import LLMServer
from gambax.llm_api.chatgpt import ChatGPT
from gambax.utils.internal import load_config


def main():

    config = load_config()

    chat_gpt = ChatGPT(model_name=config["model"])
    server = LLMServer(chat_gpt, service_config=config["services"] if "services" in config else [])
    server.run(host=config["hostname"], port=config["port"])

if __name__ == "__main__":
    main()