from typing import Literal
import json
import re

from pydantic import BaseModel
from gambax.models.ModelInterface import ModelInterface
from gambax.models.chatgpt import ChatGPT
from gambax.models.ollama import OLlama
from gambax.services import Service

SYSTEM_CALL = """
    You are ChatGPT, a large language model trained by OpenAI. 

    When you respond:
    1. You MUST call the function named "return_inline_completion_output" exactly once.
    2. The function call MUST be valid JSON, containing the fields "full_line", "line_diff", and "following_lines".
    3. The "line_diff" value MUST only include the difference in the line that is to be completed (i.e., the newly generated text for that line).
    4. You MUST NOT include any additional keys or any text outside of the JSON function call.

    Follow the OpenAI function calling specification, returning your output exclusively as valid JSON in the function call. 
"""

functions = [
    {
        "name": "return_inline_completion_output",
        "description": "Returns the structured data with the required fields.",
        "parameters": {
            "type": "object",
            "properties": {
                "full_line": {
                    "type": "string",
                    "description": "A string containing the full line."
                },
                "line_diff": {
                    "type": "string",
                    "description": "A string describing line differences."
                },
                "following_lines": {
                    "type": "string",
                    "description": "A string describing any lines that follow."
                }
            },
            "required": ["full_line", "line_diff", "following_lines"]
        }
    }
]

class InlineCompletion(Service):

    name = "inline_completion"

    def __init__(self, model_name: Literal["gpt-3.5-turbo", "gpt-4o-mini", "mistral"] = "gpt-3.5-turbo", system_call: str=SYSTEM_CALL):

        super().__init__(self.name, input_signature=["line", "context_before", "context_after", "language"], output_signature=['line_diff'])

        self.model = None
        self.setup_model(model_name)

        self.system_call = system_call

    def setup_model(self, model_name: Literal["gpt-3.5-turbo", "gpt-4o-mini"]):

        if model_name.startswith("gpt"):
            self.model = ChatGPT(model_name=model_name, max_tokens = 300)
        else:
            self.model = OLlama(model=model_name)

    def request_impl(self, line: str, context_before: str, context_after: str, language: str=None):

        if line is None or line.strip() == "" and context_before.strip() == "" and context_after.strip() == "":
            return ""
        messages = [{"role": "system", "content": self.system_call}]
        user_message = f"Lines before:\n{context_before}\n\nLine: {line}\n\nLines after:\n{context_after}" + (f"\nLanguage: {language}" if language else "")
        print(f"Input: {user_message}")
        messages.append({"role": "user", "content": user_message})
        response = self.model(messages, functions=functions, function_call={"name": "return_inline_completion_output"})
        line_diff = None
        #import ipdb; ipdb.set_trace()
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except Exception as e:
                match = re.search(r'"line_diff"\s*:\s*"([^"]*)"', response)
                line_diff = match.group(1)
        if line_diff is None:
            structured_output = response.get("arguments", {})
            if structured_output != {} and "line_diff" in structured_output:
                try:
                    structured_output = json.loads(structured_output)
                except Exception as e:
                    print("Error: Failed to parse structured output!")
                    return ""
                line_diff = structured_output["line_diff"]
        if line_diff:
            line_diff = self._parse_line_diff(line_diff, line)
            return line_diff
        return ""
    
    def _parse_line_diff(self, completion: str, line: str):
        line_diff = completion
        # Ensure line_diff is actually a diff and not the full line
        if line_diff.startswith(line):
            line_diff = line_diff[len(line):]
        else:
            line_strip = line.strip().split(' ')[-1]
            line_re = re.escape(line_strip)
            match = re.search(line_re, line_diff)
            if match:
                line_diff = line_diff[match.end():]

        print(f"Original line: '{line}'")
        print(f"Adjusted line_diff: '{line_diff}'")

        return line_diff