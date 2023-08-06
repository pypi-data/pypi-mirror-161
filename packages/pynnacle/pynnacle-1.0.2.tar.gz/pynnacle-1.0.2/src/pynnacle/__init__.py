"""Top-level package for pynnacle."""
# Core Library modules
import configparser
import json
import logging.config
from importlib import resources

# Third party modules
import yaml  # type: ignore

LOGGING_CONFIG = """
version: 1
disable_existing_loggers: False
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    stream: ext://sys.stdout
    formatter: basic
  file:
    class: logging.FileHandler
    level: DEBUG
    filename: pynnacle.log
    encoding: utf-8
    formatter: timestamp

formatters:
  basic:
    style: "{"
    format: "{levelname:s}:{name:s}:{message:s}"
  timestamp:
    style: "{"
    format: "{asctime} - {levelname} - {name} - {message}"

loggers:
  init:
    handlers: [console, file]
    level: DEBUG
    propagate: False
"""

logging.config.dictConfig(yaml.safe_load(LOGGING_CONFIG))
logger = logging.getLogger("init")


_ini_text = resources.read_text("pynnacle", "config.ini")
_ini = configparser.ConfigParser()
_ini.optionxform = str  # type: ignore
_ini.read_string(_ini_text)
ini_config = {section: dict(_ini.items(section)) for section in _ini.sections()}


__title__ = "pynnacle"
__version__ = "1.0.2"
__author__ = "Stephen R A King"
__description__ = "Utiltiy wrapper class to leverage email transmission"
__email__ = "stephen.ra.king@gmail.com"
__license__ = "MIT"
__copyright__ = "Copyright 2022 Stephen R A King"
