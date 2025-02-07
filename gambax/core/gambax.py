from typing import List

from gambax.utils import load_config, save_config
from gambax.core import LLMServer, LLMClient
from gambax.services import Service
from gambax.models import load_model

class Gambax:


    def __init__(self):

        self.config = load_config()

        model = load_model(self.config["model"])

        self.server = LLMServer(
            model = model,
            hostname = self.config["hostname"],
            port = self.config["port"],
            service_config = self.config["services"] if "services" in self.config else []
        )
        self.client = LLMClient(
            hostname = self.config["hostname"],
            port = self.config["port"]
        )

        self.server.run(run_async=True)

    def request_response(self, messages: List[str]) -> str:
        return self.client.request_response(messages)
    
    def register_service(self, service):
        self.server.register_service(service)