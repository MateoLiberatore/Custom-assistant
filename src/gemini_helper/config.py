from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = BASE_DIR / '.env'

DEFAULTS = {
    "CHATS_DIR": "chats",
    "DEFAULT_MODEL": "gemini-2.5-flash",
    "DEFAULT_TEMPERATURE": 0.5,
    "DEFAULT_SYSTEM_PROMPT": "You are a helpful and concise console assistant.",
}

def load_config():
    if DOTENV_PATH.exists():
        load_dotenv(dotenv_path=DOTENV_PATH, override=False)

    cfg = {
        "CHATS_DIR": os.getenv("CHATS_DIR", DEFAULTS["CHATS_DIR"]),
        "DEFAULT_MODEL": os.getenv("DEFAULT_MODEL", DEFAULTS["DEFAULT_MODEL"]),
        "DEFAULT_TEMPERATURE": float(os.getenv("DEFAULT_TEMPERATURE", DEFAULTS["DEFAULT_TEMPERATURE"])),
        "DEFAULT_SYSTEM_PROMPT": os.getenv("DEFAULT_SYSTEM_PROMPT", DEFAULTS["DEFAULT_SYSTEM_PROMPT"]),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
    }
    return cfg
