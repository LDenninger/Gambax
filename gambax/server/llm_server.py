import flask 
from flask import Flask, jsonify, request

from typing import List, Dict
import threading
import requests

from gambax.llm_api.ModelInterface import ModelInterface
from gambax.utils.plugin import instantiate_from_config


class LLMServer:

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

    def set_model(self, model):
        assert isinstance(model, ModelInterface), "Model must be an instance of ModelInterface"
        self.llm_model = model
    
        
    def request_response_impl(self, messages: List[str]) -> str:
        if self.llm_model is None:
            return "Server has no set LLM model"
        response = self.llm_model(messages)
        return response

    ##-- Requests --##
    def request_response(self) -> str:
        messages = request.json.get("messages")
        response = self.request_response_impl(messages)
        return jsonify({"response": response}), 200 if response is not None else 404
    
    def request_service(self, service_name: str) -> str:
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


    def run(self, host=None, port=None, debug=True, run_async=False):
        """Start the Flask server"""
        host = host if host is not None else self.hostname
        port = port if port is not None else self.port
        port = int(port)

        def _run_server():
            self.app.run(host=host, port=port, debug=debug)

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
    


