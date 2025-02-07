
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../config/gambax.json")
CHAT_FILE = os.path.join(os.path.dirname(__file__), "../config/last_chat.json")
CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "../checkpoints")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_chat():
    if not os.path.exists(CHAT_FILE):
        return []
    
    try:
        with open(CHAT_FILE, "r") as f:
            chat = json.load(f)
    except Exception as e:
        print(f"Error loading the previous chat from: {CHAT_FILE}")
        return []
    return chat

def save_chat(chat):
    with open(CHAT_FILE, "w") as f:
        json.dump(chat, f, indent=4)