import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TODOIST_API_KEY = os.getenv("TODOIST_API_KEY")
    AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini")
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "10"))  # seconds

    GEMINI_MODEL = "gemini-3.5-flash"

    MEMORY_FILE = "memory.md"


config = Config()