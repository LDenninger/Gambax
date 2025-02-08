import argparse
from pathlib import Path
import sys, os
import json
from termcolor import colored
import re
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
import speech_recognition as sr
from markdown_it import MarkdownIt


from gambax.core import LLMClient, JitLLMServer
from gambax.utils.internal import load_config, load_chat, save_chat
from gambax.interfaces.cli.command import load_commands, parse_commands
from gambax.models import load_model

CONFIG_FILE = "configs/gambax_bash.json"
VERBOSE = True

def check_connection(host='127.0.0.1', port=80):
    try:
        with socket.create_connection((host, port), timeout=5):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False

def main():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for your question...")
        audio = recognizer.listen(source)

    try:
        question = recognizer.recognize_google(audio)
        print(f"You said: {question}")
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return

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
        return
        
    messages += [{"role": "assistant", "content": response}]

    verbose_string += f"[t: {end_time - start_time:.3f}s]" if VERBOSE else ""
    console.print(Text("Assistant:", style="bold green"), end=" ")
    if VERBOSE:
        console.print(Text(verbose_string, style="dim"))

    parser = MarkdownIt()
    parsed_response = parser.render(response)
    console.print(Markdown(parsed_response))

    save_chat(messages)    

if __name__ == "__main__":
    main()
