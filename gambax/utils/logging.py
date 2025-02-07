import logging
from termcolor import colored
import functools
import os
import atexit
import sys

class _ColorfulFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        self._root_name = kwargs.pop("root_name") + "."
        self._abbrev_name = kwargs.pop("abbrev_name", "")
        if len(self._abbrev_name):
            self._abbrev_name = self._abbrev_name + "."
        super(_ColorfulFormatter, self).__init__(*args, **kwargs)

    def formatMessage(self, record):
        record.name = record.name.replace(self._root_name, self._abbrev_name)
        log = super(_ColorfulFormatter, self).formatMessage(record)
        if record.levelno == logging.WARNING:
            prefix = colored("WARNING", "yellow", attrs=["blink"])
        elif record.levelno == logging.ERROR or record.levelno == logging.CRITICAL:
            prefix = colored("ERROR", "red", attrs=["blink", "underline"])
        elif record.levelno == logging.DEBUG:
            prefix = colored("DEBUG", "yellow")
        else:
            return log
        return prefix + " " + log


@functools.lru_cache()
def setup_logger(name: str='mainlogger', color:bool=True, log_level=logging.DEBUG):
    """
        Setup logging.

        Arguments:
            name (str): Name of the logger.
            color (bool): Use colorful output.
            log_level (int): Desired log level. Defaults to logging.DEBUG.
        Returns:
            logging.Logger: The configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.handlers.clear()

    abbrev_name = 'AD'
    # stdout logging: master onlyt
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(log_level)
    if color:
        formatter = _ColorfulFormatter(
            colored("[%(asctime)s %(name)s %(levelname)s]: ", "green") + "%(message)s",
            datefmt="%m/%d %H:%M:%S",
            root_name=name,
            abbrev_name=str(abbrev_name),
        )
    else:
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s:%(lineno)d %(levelname)s: %(message)s", datefmt="%m/%d %H:%M:%S"
        )
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
