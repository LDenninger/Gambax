from abc import abstractmethod
from typing import List, Dict
from pathlib import Path
import re
import os
import subprocess
import logging 
logger = logging.getLogger("gambax")

from gambax.utils import load_chat, message_template, load_config, instantiate_from_config

class Command:
    """ 
        Command base class for CLI commands.

        Abstract Methods:
            command_impl(messages: List[Dict[str, str]], position: int, *args, **kwargs) -> str:
                Implements the command logic.

        Parameters:
            name (str): Name of the command.
            command (str): Command tag used within the question, e.g. '\\cc'
            description (str): Description of the command.

    """

    def __init__(self, name: str, command: str=None, description: str = ""):

        
        self.name = name
        self.command = command or self.name
        self.description = description

        self._cmd_last_char = None

    def __call__(self, messages, position, *args, **kwargs) -> str:
        return self.command_impl(messages, position, *args, **kwargs)
    @abstractmethod
    def command_impl(self, messages, position, *args, **kwargs) -> str:
        raise NotImplementedError("'command_impl()' must be defined by implemented commands.")

    def cut_command(self, question: str, position: int, end_position = None) -> str:
        end_position = end_position or self._cmd_last_char or position + len(self.command) + 2
        return question[:position] + question[end_position:]

    def insert_text(self, question: str, position: int, text: str) -> str:
        return question[:position] + text + question[position:]

    def get_arguments(self, text):
        pattern = r"\{(.*?)\}"
        match = re.search(pattern, text)
        self._cmd_last_char = match.end() if match else None
        arguments = match.group(1).split(',')
        return arguments

    def __str__(self):
        return self.name
    

class ContinueChatCommand(Command):

    def __init__(self):
        super().__init__('continue_chat', 'cc', 'Continue the chat.')


    def command_impl(self, messages: List[Dict[str, str]], position: int):
        chat = load_chat()
        last_message = self.cut_command(messages[-1]['content'], position)
        last_message = message_template("user", last_message)
        chat.append(last_message)
        return chat

class InsertFileCommand(Command):

    def __init__(self, allowed_files: List[str] = [".py", ".txt", ".md", ".cpp", ".sh", ".java"]):
        super().__init__('insert_file', 'insert', 'Insert a file into the chat.')
        self.allowed_files = allowed_files

    def command_impl(self, messages: List[Dict[str, str]], position: int):
        question = messages[-1]['content']
        arguments = self.get_arguments(question[position:])
        path = Path(arguments[0].strip())
        content = ""
        if path.is_file():
            try:
                with open(path, "r") as file:
                    content = file.read()
            except FileNotFoundError:
                print(f"Error: File '{path}' not found.")
                return question, False
        else:
            # Load all files from the path up to a depth of 2 into a dictionary
            file_dict = {}
            for root, _, files in os.walk(path, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if Path(file_path).suffix not in self.allowed_files:
                        continue
                    file_dict[file_path] = open(file_path, "r").read()
            content = "\n\n".join(f"{name}: \n{content}" for name, content in file_dict.items())

        question = self.cut_command(question, position) 
        question = self.insert_text(question, position, f"\n{content}\n")
        messages[-1]["content"] = question
        return messages

class SilverSearcherCommand(Command):

    def __init__(self, allowed_files: List[str] = [".py", ".txt", ".md", ".cpp", ".sh", ".java"]):
        super().__init__('silver_searcher', 'ag', 'Search for files using SilverSearcher.')
        self.allowed_files = allowed_files

    def command_impl(self, messages: List[Dict[str, str]], position: int):
        question = messages[-1]['content']
        arguments = self.get_arguments(question[position:])
        search_string = arguments[0].strip()

        result = subprocess.run(" ".join(["ag", f"'{search_string}'", f"{os.getcwd()}"]), shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split("\n")

        content = ""
        for file in files:
            file = file.split(":")[0]
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content += f"\n\n{file}\n{f.read()}"
            except FileNotFoundError:
                print(f"Error: File '{file}' not found.")
                continue
        
        question = self.cut_command(question, position)
        question = self.insert_text(question, position, f"\n{content}\n")

        messages[-1]["content"] = question
        return messages

class ExecuteCommand(Command):

    def __init__(self, include_file: bool = True):

        super().__init__('execute', 'exec', 'Execute a command.')

        self.include_file = include_file
        
    def command_impl(self, messages: List[Dict[str, str]], position: int):
        question = messages[-1]['content']
        arguments = self.get_arguments(question[position:])
        run_cmd = " ".join(arguments)
        logger.info(f"Executing command: {run_cmd}")
        result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
        content = f"Command: {run_cmd}\n"
        if self.include_file:
            run_cmd_split = run_cmd.split(" ")
            file_name = None
            if os.path.exists(run_cmd_split[0]):
                file_name = run_cmd_split[0]
            elif len(run_cmd_split)>1 and os.path.exists(run_cmd_split[1]):
                file_name = run_cmd_split[1]
            if file_name:
                try:
                    with open(file_name, "r", encoding="utf-8") as f:
                        content += f"File: {run_cmd_split[1]}"
                        content += f"\n{f.read()}\n"
                except Exception as e:
                    logger.error(f"Error reading file '{file_name}': {str(e)}")
        
        content += f"Stdout:\n{result.stdout}\nStderr:\n{result.stderr}"
        message = message_template("user", content)
        messages.insert(-2, message)

        return messages
        

def parse_commands(messages: List[Dict[str, str]], commands: List[Command]) -> List[Dict[str, str]]:
    for p in re.finditer(r"\\", messages[-1]['content']):

        cmd = messages[-1]['content'][p.start()+1:].split(' ')[0].split("{")[0]
        command = next((c for c in commands if c.command == cmd), None)
        if command:
            messages = command(messages, p.start())
    
    return messages

def load_commands() -> List[Command]:
    config = load_config()
    commands = [instantiate_from_config(conf) for conf in config["commands"]]
    return commands