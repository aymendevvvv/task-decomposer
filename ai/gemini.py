# ai/gemini_provider.py

from google import genai
from google.genai import types

from config import config
from ai.base import AIProvider


def _log(message):
    print(f"[gemini] {message}", flush=True)


class GeminiProvider(AIProvider):

    def __init__(self):
        self.client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.model = config.GEMINI_MODEL

    def build_prompt(self, task):
        return f"""
Break the following task into ADHD-friendly steps.

Rules:
- Determine the number of steps based on the task's complexity and difficulty. 
- You MUST generate between 3 and 8 steps. No more, no less.
- Simple tasks should have fewer steps (e.g., 3-4), while complex tasks should have more (e.g., 6-8).
- Each step should take less than 10 minutes to complete.
- Be very specific and actionable.
- Start each step with a strong verb.
- Include a relevant emoji at the start of each step.
- Return ONLY a numbered list of steps.

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
        _log("Generating subtasks")
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

        steps = self.parse(response_text)
        _log(f"Generated {len(steps)} parsed subtask(s)")
        return steps

    def summarize_task(self, task: str) -> str:
        _log("Summarizing task title")
        prompt = f"""
Summarize this task into a very short, punchy title (max 6-8 words).
The goal is to display it in a small UI header.

Task: "{task}"

Summary:
"""
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )

        summary = response.text.strip().strip("*")
        _log(f"Summary ready: {summary}")
        return summary
