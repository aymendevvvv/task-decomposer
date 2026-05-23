# ai/factory.py

from config import config
from ai.gemini import GeminiProvider


def get_ai_provider():
    if config.AI_PROVIDER == "gemini":
        return GeminiProvider()

    raise ValueError(f"Unsupported AI provider: {config.AI_PROVIDER}")