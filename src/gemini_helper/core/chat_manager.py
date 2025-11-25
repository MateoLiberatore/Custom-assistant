from pathlib import Path
import json
import re
from datetime import datetime
from typing import List, Tuple

from ..constants import CHATS_DIR, DEFAULT_SYSTEM_PROMPT, DEFAULT_TEMPERATURE, METADATA_START_TAG, METADATA_END_TAG
from ..utils.filesystem import ensure_dir
from ..utils.parsing import clean_filename 

class ChatManager:
    def __init__(self):
        ensure_dir(CHATS_DIR)
        self.name = ""
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.temperature = DEFAULT_TEMPERATURE
        self.history = []
        self.is_saved = False

    def new_chat(self):
        self.name = ""
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.temperature = DEFAULT_TEMPERATURE
        self.history = []
        self.is_saved = False

    def set_name(self, name: str):
        self.name = clean_filename(name)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})

    def save_chat(self, gemini_history: List[dict]) -> str:
        if not self.name:
            return "ERROR: Chat has no name. Use #name first."

        file_path = Path(CHATS_DIR) / f"{self.name}.txt"

        metadata = {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "saved_at": datetime.now().isoformat(),
            "gemini_history": [item for item in gemini_history]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"{METADATA_START_TAG}\n")
            f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
            f.write(f"\n{METADATA_END_TAG}\n\n")

            for msg in self.history:
                f.write(f"[{msg['role']}] {msg['content']}\n")

        self.is_saved = True
        return f"Chat '{self.name}' saved successfully."

    def load_chat(self, chat_name: str) -> Tuple[dict, list]:
        file_path = Path(CHATS_DIR) / f"{chat_name}.txt"
        if not file_path.exists():
            raise FileNotFoundError(f"Chat '{chat_name}' does not exist.")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        meta_match = re.search(f"{METADATA_START_TAG}\\n(.*)\\n{METADATA_END_TAG}", content, re.DOTALL)
        if not meta_match:
            raise ValueError("Invalid file format: Missing metadata.")

        metadata = json.loads(meta_match.group(1).strip())

        self.name = metadata.get("name", chat_name)
        self.system_prompt = metadata.get("system_prompt", DEFAULT_SYSTEM_PROMPT)
        self.temperature = metadata.get("temperature", DEFAULT_TEMPERATURE)
        self.is_saved = True

        gemini_history = metadata.get("gemini_history", [])

        # reconstruct minimal history for display
        self.history = [
            {"role": item.get('role', 'MODEL'), "content": (item.get('parts', [{'text': ''}])[0].get('text', '')), "timestamp": ''}
            for item in gemini_history if item.get('role') != 'system'
        ]

        return metadata, gemini_history

    def get_all_chats(self) -> List[dict]:
        chats_list = []
        for file in Path(CHATS_DIR).glob("*.txt"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                meta_match = re.search(f"{METADATA_START_TAG}\\n(.*)\\n{METADATA_END_TAG}", content, re.DOTALL)
                if meta_match:
                    metadata = json.loads(meta_match.group(1).strip())
                    chats_list.append({
                        "name": file.stem,
                        "role": metadata.get("system_prompt", ""),
                        "saved_at": metadata.get("saved_at", "Unknown")
                    })
            except Exception:
                continue
        return chats_list

    def get_filtered_chats(self, query: str) -> List[dict]:
        all_chats = self.get_all_chats()
        if not query:
            return all_chats
        q = query.lower()
        return [c for c in all_chats if q in c['name'].lower() or q in c['role'].lower()]

    def delete_chat(self, chat_name: str) -> str:
        file_path = Path(CHATS_DIR) / f"{chat_name}.txt"
        if file_path.exists():
            file_path.unlink()
            return f"Chat '{chat_name}' deleted."
        return f"ERROR: Chat '{chat_name}' not found."
