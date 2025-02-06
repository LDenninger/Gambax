
import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "../config/gambax.json")

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)
    
def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)