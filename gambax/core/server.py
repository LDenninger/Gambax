import flask 
from flask import Flask, jsonify, request

from typing import List, Dict
import threading
import requests
import json
from termcolor import colored

from gambax.models import load_model
from gambax.models.ModelInterface import ModelInterface
from gambax.utils.plugin import instantiate_from_config
from gambax.utils.logging import setup_logger
from gambax.utils.internal import load_config, save_config
from gambax.services import Service, ServiceWrapper

class LLMServer:
    """
        The LLM server exposes a locally hosted or remote LLM
        to the local network using a Flask server.

        Requests:
            '/request_response'
    """

    def __init__(self,
                 model: ModelInterface = None,
                 hostname: str= "0.0.0.0",
                 port: str= "5000",
                 config_file: str= "config.json",
                 service_config: List[Dict[str, str]] = []
                 ):
        
        self.app = Flask("LLM Server")
        self.hostname = hostname
        self.port = port
        self.config_file = config_file

        self.logger = setup_logger("LLMServer")

        self.server_thread = None

        self.services = {}

        self.llm_model = None
        self._setup_routes()
        if model is not None:
            self.set_model(model)

        self._setup_services(service_config)

    def _setup_routes(self):
        self.app.add_url_rule('/request_response', methods=['POST'], view_func=self.request_response)
        self.app.add_url_rule('/request_service/<service_name>', methods=['POST'], view_func=self.request_service)

    def _setup_services(self, service_config: List[Dict[str, str]]):
        for service in service_config:
            target = instantiate_from_config(service)
            if target is not None:
                self.services[target.name] = target
            print(f"Registered service: {service['target']}")

    def register_service(self, service: Service):
        service_name = service.name
        self.services[service_name] = service

    def set_model(self, model):
        assert isinstance(model, ModelInterface), "Model must be an instance of ModelInterface"
        self.llm_model = model
        self.logger.info(f"Setup model {str(self.llm_model)}.")
    
    def request_response_impl(self, messages: List[str]) -> str:
        if self.llm_model is None:
            return "Server has no set LLM model"
        
        tools = []
        for n, s in self.services.items():
            tool_def = s.get_tool()
            if tool_def:
                tools.append(tool_def)

        response = self.llm_model(messages, tools=tools)
        response = self.check_service_call(response)

        return response

    def request_response(self) -> str:
        self.logger.debug(f"Response request from '{request.remote_addr}'")
        try:
            messages = request.json.get("messages")
            response = self.request_response_impl(messages)
        except Exception as e:
            return jsonify({"response": str(e)}), 401
        
        return jsonify({"response": response}), 200 if response is not None else 404
    
    def request_service(self, service_name: str) -> str:
        self.logger.debug(f"Service '{service_name}' request from '{request.remote_addr}'")
        if service_name not in self.services:
            return jsonify({"error": f"Service '{service_name}' not found"}), 401
        try:
            service_func = self.services[service_name]
        except Exception as e:
            print(f"Error calling service '{service_name}': {str(e)}")
            return jsonify({"error": f"Error starting service '{service_name}': {str(e)}"}), 500
        try:
            service_output = service_func(**request.json)
        except Exception as e:
            return jsonify({"error": f"Error executing service '{service_name}': {str(e)}"}), 500
        return jsonify({"response": service_output}), 200

    def check_service_call(self, response) -> bool:

        if isinstance(response, str):
            return response
        if "function" in response and "arguments" in response:
            service = [s for n, s in self.services.items() if s.name == response["function"]][0]
            if service:
                args = json.loads(response["arguments"]) if isinstance(response["arguments"], str) else response["arguments"]
                return service(**args)
        return ""

    def run(self, host=None, port=None, debug=True, run_async=False):
        """Start the Flask server"""
        host = host if host is not None else self.hostname
        port = port if port is not None else self.port
        port = int(port)

        def _run_server():
            self.app.run(host=host, port=port, debug=debug)
        
        self.logger.info(f"Starting LLMServer at '{host}:{port}'")
        if run_async:
            self.server_thread = threading.Thread(target=_run_server, args=())
            self.server_thread.start()
        else:
            _run_server()

    def __del__(self):
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()


class LLMClient:

    def __init__(self,
                 hostname: str= "0.0.0.0",
                 port: str= "5000",
                 ):
        self.hostname = hostname
        self.port = port

    def request_response(self, messages: List[str]) -> str:
        url = f"http://{self.hostname}:{self.port}/request_response"
        response = requests.post(url, json={"messages": messages})
        return response.json().get("response")
    
    def request_service(self, service_name: str, payload: dict) -> dict:
        url = f"http://{self.hostname}:{self.port}/request_service/{service_name}"
        response = requests.post(url, json=payload)
        return response.json()
    


def launch_server():
    config = load_config()
    model = load_model(config["model"])
    server = LLMServer(model, service_config=config["services"] if "services" in config else [])
    server.run(host=config["hostname"], port=config["port"])