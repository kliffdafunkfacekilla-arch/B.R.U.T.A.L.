import os
import json
import google.generativeai as genai
from typing import Optional

class LLMGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if self.api_key != "dummy_key":
            genai.configure(api_key=self.api_key)
            # Standard model for narrative
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            # Configured model for structured JSON output
            self.json_model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None
            self.json_model = None

    async def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """Generates immersive text for the player."""
        if self.model:
            try:
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = await self.model.generate_content_async(full_prompt)
                return response.text
            except Exception as e:
                print(f"[LLM ERROR]: {e}")
        return "The shadows shift as you act, though the outcome is clouded in mystery."

    async def generate_json(self, user_text: str, schema_prompt: str) -> str:
        """Generates reliable JSON using Gemini's response_mime_type."""
        if self.json_model:
            try:
                full_prompt = f"{schema_prompt}\n\nUser Input: {user_text}"
                response = await self.json_model.generate_content_async(full_prompt)
                return response.text
            except Exception as e:
                print(f"[LLM JSON ERROR]: {e}")

        # Fallback mock for local testing
        if "attack" in user_text.lower():
            return '{"action": "attack", "target": "goblin_01"}'
        return '{"action": "explore", "target": "room"}'
