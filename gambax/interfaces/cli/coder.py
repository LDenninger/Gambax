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
from termcolor import colored
from yaspin import yaspin
from rich.syntax import Syntax
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.rule import Rule
import pyperclip


from gambax.core import LLMClient
from gambax.utils.internal import load_config, load_chat, save_chat
from gambax.interfaces.cli.command import load_commands, parse_commands

CONFIG_FILE = "configs/gambax_bash.json"
ALLOWED_FILES = [".py", ".txt", ".md", ".cpp", ".sh", ".java"]
VERBOSE = True


def extract_url(string):
    url_pattern = r'(https?://[^\s]+)'
    match = re.search(url_pattern, string)
    return match.group(0) if match else None

    
def main():
    question = " ".join(sys.argv[1:])
    config = load_config()

    chat_client = LLMClient(hostname=config["hostname"], port=config["port"])

    service_args = {
        "prompt": question,
        "context": ""
    }
    explanation = None
    code = None
    try:
        start_time = time.time()
        with yaspin(text="Generating Code...", color="yellow") as spinner:
            response = chat_client.request_service("gambax_coder", service_args)
            response = response['response']
            if 'explanation' in response:
                explanation = response["explanation"]
            if 'code' in response:
                code = response["code"]
        end_time = time.time()
    except Exception as e:
        print(colored(f"Request to server failed! Is server running?", "red"))
        return
    console = Console()
    # Print User Prompt
    console.print(Text("User:", style="bold yellow"), end=" ")
    console.print(question)

    # Verbose timing info (if enabled)
    verbose_string = f"[t: {end_time - start_time:.3f}s] " if VERBOSE else ""

    # Print Assistant Response
    console.print(Text("Assistant:", style="bold green"), end=" ")
    console.print(verbose_string, style="dim")

    # Print Explanation (if available)
    if explanation:
        console.print(explanation, style="italic cyan")

    # Fancy Horizontal Separator
    console.print(Rule(style="bold cyan"))

    # Syntax Highlighted Code Block
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)

    # Another Horizontal Separator
    console.print(Rule(style="bold cyan"))

    pyperclip.copy(code)


if __name__ == "__main__":
    main()