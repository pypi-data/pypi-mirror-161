import os
import tomli

# Version package
__version__ = "1.0.0"

# Read URL and TOKEN from config file
with open(f"{os.path.expanduser('~')}/.yjira/config.toml", "rb") as f:
    _cfg = tomli.load(f)
    URL = _cfg["yjira"]["url"]
    TOKEN = _cfg["yjira"]["token"]
