# ai/gemini_provider.py

from google import genai
from google.genai import types

from config import config
from ai.base import AIProvider


class GeminiProvider(AIProvider):

    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.GEMINI_MODEL

    def build_prompt(self, task):
        return f"""
Break this task into 5-8 ADHD-friendly steps.

Rules:
- Each step < 10 minutes
- Very specific
- Start with a verb
- Return ONLY a numbered list

Task: "{task}"
"""

    def parse(self, text):
        steps = []
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            if "." in line:
                line = line.split(".", 1)[-1].strip()

            steps.append(line)

        return steps

    def generate_steps(self, task: str) -> list[str]:
        prompt = self.build_prompt(task)

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        response_text = ""

        for chunk in self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
        ):
            if chunk.parts and chunk.parts[0].text:
                response_text += chunk.parts[0].text

        return self.parse(response_text)