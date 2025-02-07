from gambax.utils.internal import load_config, save_config

import logging
logger = logging.getLogger("gambax")

def set_config(key, value):
    config = load_config()
    if key not in config:
        logger.error(f"Config '{key}' not recognized!")
        return False
    config[key] = value
    save_config(config)
    return True