import flask 
from flask import Flask, jsonify, request

from typing import List

from llm_api.ModelInterface import ModelInterface


class LLMServer:

    def __init__(self,
                 hostname: str= "localhost",
                 port: str= "5000",
                 config_file: str= "config.json"):
        
        self.app = Flask("LLM Server")
        self.hostname = hostname
        self.port = port
        self.config_file = config_file

        self.services = {}

        self.llm_model = None

    def _setup_routes(self):

        self.app.add_url_rule('/request_response', methods=['POST'], view_func=self.request_response)
        self.app.add_url_rule('/request_service/<service_name>', methods=['POST'], view_func=self.request_service)

    def set_model(self, model):
        assert isinstance(model, ModelInterface), "Model must be an instance of ModelInterface"
        self.llm_model = model
        
    def request_response_impl(self, messages: List[str]) -> str:
        return ""


    def request_response(self) -> str:
        messages = request.json.get("messages")
        response = self.request_response_impl(messages)
        return jsonify({"response": response}), 200 if response is not None else 404
    
    def request_service(self, service_name: str) -> str:
        if service_name not in self.services:
            return jsonify({"error": f"Service '{service_name}' not found"}), 404
        
        service_func = self.services[service_name]
        try:
            service_output = service_func(**request.json)
        except Exception as e:
            return jsonify({"error": f"Error executing service '{service_name}': {str(e)}"}), 500
        
        return jsonify(service_output), 200








