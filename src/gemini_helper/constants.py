from .config import load_config
_cfg = load_config()

CHATS_DIR = _cfg["CHATS_DIR"]
DEFAULT_MODEL = _cfg["DEFAULT_MODEL"]
DEFAULT_TEMPERATURE = _cfg["DEFAULT_TEMPERATURE"]
DEFAULT_SYSTEM_PROMPT = _cfg["DEFAULT_SYSTEM_PROMPT"]

METADATA_START_TAG = "# METADATA_START"
METADATA_END_TAG = "# METADATA_END"

COMMANDS = {
    "#save": "Saves the current conversation.",
    "#name": "Assigns/changes the name of the current chat (Ex: #name my_project).",
    "#menu": "Opens the application's main menu.",
    "#delete": "Deletes the current chat (if saved) and starts a new one.",
    "#new": "Starts a new conversation (after a warning if unsaved).",
    "#help": "Shows this list of commands.",
    "#chats": "Opens the chat history menu (with search).",
    "#role": "Sets the assistant's role/context (Ex: #role You are a pirate).",
    "#temp": "Adjusts the temperature (creativity) [0.0 - 1.0] (Ex: #temp 0.8).",
    "#exit": "Closes the application."
}
