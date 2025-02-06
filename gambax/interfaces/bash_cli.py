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

from gambax.server import LLMClient
from gambax.utils.internal import load_config


CONFIG_FILE = "configs/gambax_bash.json"
ALLOWED_FILES = [".py", ".txt", ".md", ".cpp", ".sh", ".java"]
VERBOSE = True

def parse_question(question):

    # Find all positions that match // 
    positions = [m.start() for m in re.finditer(r"\\", question)]
    if not positions:
        return question
    # Extract the comments and their positions
    comments = [question[pos:].strip() for pos in positions[::2]]
    positions = positions[1::2]

    for p in re.finditer(r"\\", question):
        position_start = p.start()
        cmd = question[position_start+1:].split(' ')[0].split("{")[0]
        position_end = position_start + len(cmd)

        if cmd.lower() == "insert":
            # Find that {} brackets behind the command and get the text inside
            pattern = r"\{(.*?)\}"
            match = re.search(pattern, question[position_start:])
            arguments = match.group(1).split(',')

            path = Path(arguments[0].strip())
            content = ""
            if path.is_file():
                try:
                    with open(path, "r") as file:
                        content = file.read()
                except FileNotFoundError:
                    print(f"Error: File '{path}' not found.")
                    return question, []
            else:
                # Load all files from the path up to a depth of 2 into a dictionary
                file_dict = {}
                for root, _, files in os.walk(path, topdown=False):
                    for name in files:
                        file_path = os.path.join(root, name)
                        if Path(file_path).suffix not in ALLOWED_FILES:
                            continue
                        file_dict[file_path] = open(file_path, "r").read()
                content = "\n\n".join(f"{name}: \n{content}" for name, content in file_dict.items())
            
            question = question[:position_start] + f"\n{content}\n" + question[match.end():]
        elif cmd.lower() == "ag":
            pattern = r"\{(.*?)\}"
            match = re.search(pattern, question[position_start:])
            arguments = match.group(1).split(',')
            search_string = arguments[0].strip()

            result = subprocess.run(" ".join(["ag", f"'{search_string}'", f"{os.getcwd()}"]), shell=True, capture_output=True, text=True)
            files = result.stdout.strip().split("\n")

            # Read and print content from each file
            content = ""
            for file in files:
                file = file.split(":")[0]
                try:
                    with open(file, "r", encoding="utf-8") as f:
                        content += f"\n\n{file}\n{f.read()}"
                except FileNotFoundError:
                    print(f"Error: File '{file}' not found.")
                    continue
            question = question[:position_start] + f"\n{content}\n" + question[match.end():]

    return question

    
def main():
    question = " ".join(sys.argv[1:])
    question = parse_question(question)

    config = load_config()


    chat_client = LLMClient(hostname=config["hostname"], port=config["port"])

    system_call = config["system_call"]

    messages = [
        {"role": "system", "content": system_call},
        {"role": "user", "content": question}
    ]
    start_time = time.time()
    response = chat_client.request_response(messages)
    end_time = time.time()
    print(colored("Question:", "yellow"))
    print(question)
    verbose_string = f"[t: {end_time - start_time:.3f}s] " if VERBOSE else ""
    print(colored("Assistant:", "green") + verbose_string)

    parser = MarkdownIt(renderer_cls=RendererPlain)
    response = parser.render(response)
    print(response)


if __name__ == "__main__":
    main()