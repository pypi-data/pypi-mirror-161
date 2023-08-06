import re

# import class
from .database import *
from .exceptions import *
from .time import *

from .log import log
from .mqtt import Mqtt

__all__ = [
    # export module
    "mqtt",
    "exceptions",
    "database",
    # export class
    "Mqtt",
    "log",
    "time",
]


try:
    with open("pyproject.toml", "r") as f:
        __version__ = re.search(
            r'^version\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
        ).group(1)
except FileNotFoundError:
    __version__ = "0.3.1"
