import ollama
from gambax.models import ModelInterface
import subprocess
from typing import List
import copy
import requests
import json

from gambax.utils import setup_logger

def is_ollama_running(hostname: str, port:int):
    try:
        response = requests.get(f"http://{hostname}:{port}/api/tags", timeout=2)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

class OLlama(ModelInterface):
    def __init__(self, 
                 model: str = "mistral",
                 ollama_host: str = "0.0.0.0",
                 ollama_port: int = 11434
                 ):
        super().__init__("OLlama")
        self.model = model
        self.ollama_host = ollama_host
        self.ollama_port = ollama_port
        self.logger = setup_logger("OLlama")
        self._backend_process = None
        self._setup_model()

    def call_impl(self, messages: List[str], *args, **kwargs) -> str:
        #import ipdb; ipdb.set_trace()
        is_tool_call = False
        if 'functions' in kwargs:
            is_tool_call = True
            kwargs['tools'] = copy.deepcopy(kwargs['functions'])
            del kwargs["functions"]
            del kwargs["function_call"]
        response = ollama.chat("mistral", messages=messages,*args, **kwargs)
        response = response.message.content
        return response

    def _setup_model(self):

        # Check whether a backend process is already running
        if is_ollama_running(self.ollama_host, self.ollama_port):
            return
        ollama_pull_cmd = f"ollama pull {self.model}"
        self.logger.info(f"Pulling OLlama model '{self.model}'...")
        result = subprocess.run(ollama_pull_cmd, shell=True, check=True)
        if result.returncode != 0:
            raise Exception(f"Failed to pull OLlama model '{self.model}': {result.stderr}")
        ollama_launch_cmd = f"OLLAMA_HOST={self.ollama_host} OLLAMA_PORT={self.ollama_port} ollama serve {self.model}"
        self._backend_process = subprocess.Popen(ollama_launch_cmd, shell=True)
        ollama.host = f"http://{self.ollama_host}:{self.ollama_port}"


    def __del__(self):
        if self._backend_process:
            self._backend_process.terminate()
            self._backend_process.wait()