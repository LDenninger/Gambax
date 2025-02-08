import argparse
from pathlib import Path
import sys, os
sys.path.append(os.getcwd())
import json
from termcolor import colored
import re
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain
import subprocess
import time
import webbrowser
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.rule import Rule
from yaspin import yaspin
import pyperclip
import socket

from gambax.core import LLMClient, JitLLMServer
from gambax.utils.internal import load_config, load_chat, save_chat
from gambax.interfaces.cli.command import load_commands, parse_commands
from gambax.models import load_model

CONFIG_FILE = "configs/gambax_bash.json"
ALLOWED_FILES = [".py", ".txt", ".md", ".cpp", ".sh", ".java"]
VERBOSE = True


def extract_url(string):
    url_pattern = r'(https?://[^\s]+)'
    match = re.search(url_pattern, string)
    return match.group(0) if match else None

def check_connection(host='127.0.0.1', port=80):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    
def main():
    question = " ".join(sys.argv[1:])
    config = load_config()
    verbose_string = ""
    if check_connection(config["hostname"], config["port"]):
        chat_client = LLMClient(hostname=config["hostname"], port=config["port"])
        verbose_string += f"[server: '{config['hostname']}:{config['port']}']"
    else:
        model = load_model(config["model"])
        chat_client = JitLLMServer(model=model, service_config=config["services"] if "services" in config else [])
        verbose_string += "[server: off]"
    commands = load_commands()

    system_call = config["system_call"]

    console = Console()

    messages = [
        {"role": "system", "content": system_call},
        {"role": "user", "content": question}
    ]
    messages = parse_commands(messages, commands)
    try:
        start_time = time.time()
        with yaspin(text="Gambax is thinking of a response...", color="yellow") as spinner:
            response = chat_client.request_response(messages)
        end_time = time.time()
    except Exception as e:
        console.print(Text("Request failed! Error in server-client connection. Please re-try...", style="bold red"))
        
    messages += [{"role": "assistant", "content": response}]

    # Print User Prompt
    #console.print(Text("User:", style="bold yellow"), end=" ")
    #console.print(question)

    # Verbose timing info (if enabled)
    verbose_string += f"[t: {end_time - start_time:.3f}s]" if VERBOSE else ""
    # Print Assistant Response
    console.print(Text("Assistant:", style="bold green"), end=" ")
    if VERBOSE:
        console.print(Text(verbose_string, style="dim"))

    # Extract and open URL if present
    #url = extract_url(response)
    #if url:
    #    webbrowser.open(url)
    #    console.print(f"[bold blue]🔗 Opened URL:[/] {url}")

    # Parse Markdown response
    parser = MarkdownIt(renderer_cls=RendererPlain)
    parsed_response = parser.render(response)

    # Check for code blocks and display accordingly
    if "```" in response:
        code_blocks = response.split("```")

        largest_code_block = ""

        
        for i, block in enumerate(code_blocks):
            if i % 2 == 0:  # Normal text (Markdown)
                console.print(Markdown(block.strip(), code_theme="monokai"))
            else:  # Code block
                if block.startswith("\n"):
                    language = "plaintext"
                else:
                    language = block.split("\n")[0]
                    block = "\n".join(block.split("\n")[1:])
                syntax = Syntax(block.strip(), language, theme="monokai", line_numbers=True)
                console.print(syntax)

                if len(block) > len(largest_code_block):
                    largest_code_block = block
    else:
        console.print(Markdown(parsed_response, code_theme="monokai"))

    if largest_code_block != "":
        pyperclip.copy(largest_code_block)
    # Add horizontal separator for clarity
    save_chat(messages)    

if __name__ == "__main__":
    main()