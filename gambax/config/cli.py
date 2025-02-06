import sys
from gambax.utils.internal import load_config, save_config

def main():
    config = load_config()

    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: gambax-config <key> <value>")
        print("Config:")
        print("\n ".join(f"{key}: {value}" for key, value in config.items()))

    key = args[0]
    value = " ".join(args[1:])
    config[key] = value

    save_config(config)

    print(f"Updated config for '{key}': {value}")

if __name__ == "__main__":
    main()