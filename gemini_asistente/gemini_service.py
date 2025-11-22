from google import genai
from google.genai.errors import APIError
from .constants import DEFAULT_MODEL
import os # <--- New: Required to read the key from the environment

class GeminiChatService:
    def __init__(self, system_prompt: str, temperature: float, history: list = None):
        # The client initialization is done here
        self.client = self._initialize_client() 
        self.chat = None
        self.config = {
            "system_prompt": system_prompt,
            "temperature": temperature
        }
        self.history_is_loaded = False
        
        self.update_config()
        if history:
            self.load_history(history)
            
    def _initialize_client(self):
        api_key = os.getenv("GEMINI_API_KEY") 
        
        # 1. Key loaded validation
        if not api_key:
             raise EnvironmentError("GEMINI_API_KEY is not configured or the .env file was not loaded correctly.")

        try:
            return genai.Client(api_key=api_key) 
        except Exception as e:
            # If it fails here, it means the key itself is invalid or rejected by the server.
            print(f"Underlying client error: {e}")
            raise EnvironmentError("GEMINI_API_KEY is configured, but client initialization failed (possibly invalid key or API issue).")
            

    def update_config(self, system_prompt: str = None, temperature: float = None):
        if system_prompt is not None:
            self.config["system_prompt"] = system_prompt
        if temperature is not None:
            self.config["temperature"] = temperature

        self.chat = self.client.chats.create(
            model=DEFAULT_MODEL,
            config={
                "system_instruction": self.config["system_prompt"],
                "temperature": self.config["temperature"]
            }
        )
        self.history_is_loaded = False

    def load_history(self, history: list):
        try:
            self.chat.restore(history)
            self.history_is_loaded = True
        except Exception as e:
            raise ValueError(f"Error loading chat history: {e}")

    def send_message(self, message: str) -> str:
        if not self.client:
             raise EnvironmentError("Gemini client not initialized.")
             
        try:
            response = self.chat.send_message(message)
            return response.text
        except APIError as e:
            return f"API Error: {e}"
        except Exception as e:
            return f"Unexpected error: {e}"

    def get_full_history(self) -> list:
        if not self.chat or not self.chat.history:
            return []
        
        return self.chat.history