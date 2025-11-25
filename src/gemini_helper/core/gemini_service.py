import os
from typing import List

from ..constants import DEFAULT_MODEL

try:
    from google import genai
    from google.genai.errors import APIError
except Exception:
    genai = None
    APIError = Exception

class GeminiChatService:
    def __init__(self, system_prompt: str, temperature: float, api_key: str = None, history: List[dict] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.client = None
        self.chat = None
        self.config = {"system_prompt": system_prompt, "temperature": temperature}
        self.history_is_loaded = False

        if self.api_key and genai:
            self._initialize_client()
            self.update_config()
            if history:
                self.load_history(history)

    def _initialize_client(self):
        if not self.api_key:
            raise EnvironmentError("GEMINI_API_KEY is not configured.")
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise EnvironmentError(f"Client initialization failed: {e}")

    def update_config(self, system_prompt: str = None, temperature: float = None):
        if system_prompt is not None:
            self.config['system_prompt'] = system_prompt
        if temperature is not None:
            self.config['temperature'] = temperature

        if not self.client:
            return

        self.chat = self.client.chats.create(
            model=DEFAULT_MODEL,
            config={
                "system_instruction": self.config['system_prompt'],
                "temperature": self.config['temperature']
            }
        )
        self.history_is_loaded = False

    def load_history(self, history: List[dict]):
        if not self.chat:
            return
        try:
            self.chat.restore(history)
            self.history_is_loaded = True
        except Exception as e:
            raise ValueError(f"Error loading chat history: {e}")

    def send_message(self, message: str) -> str:
        if not self.chat:
            return "[Offline Mode] — client not initialized or API key missing."
        try:
            resp = self.chat.send_message(message)
            return getattr(resp, 'text', str(resp))
        except APIError as e:
            return f"API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def get_full_history(self) -> List[dict]:
        if not self.chat:
            return []
        return getattr(self.chat, 'history', [])
