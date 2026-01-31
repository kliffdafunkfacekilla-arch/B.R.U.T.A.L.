# This is a stub. In production, use 'openai' or 'google-generativeai' libraries.
import google.generativeai as genai
import os
import json

class LLMGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        if self.api_key != "dummy_key":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

    async def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """
        Used for the Storyteller / Micro-Generator.
        Returns pure text for the TTS to read.
        """
        if self.model:
            try:
                # Gemini doesn't have system prompts in the same way as OpenAI, but we can prepend it
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = await self.model.generate_content_async(full_prompt)
                return response.text
            except Exception as e:
                print(f"[LLM ERROR]: {e}")

        print(f"\n[AI THOUGHTS]: Processing Narrative (Simulated)...")
        return "Simulated Narrative: The goblin shrieks as your sword connects!"

    async def generate_json(self, user_text: str, schema_prompt: str) -> str:
        """
        Used for the Intent Parser and Macro-Generator.
        Forces the model to output valid JSON.
        """
        if self.model:
            try:
                # Force JSON output via prompting
                full_prompt = f"{schema_prompt}\n\nUser Input: {user_text}\n\nEnsure the output is valid JSON without markdown formatting."
                response = await self.model.generate_content_async(full_prompt)
                text = response.text
                # cleanup markdown code blocks if present
                if text.startswith("```json"):
                    text = text[7:]
                if text.endswith("```"):
                    text = text[:-3]
                return text.strip()
            except Exception as e:
                print(f"[LLM ERROR]: {e}")

        print(f"\n[AI THOUGHTS]: Parsing Intent (Simulated)...")
        # Simulating a return for the 'attack' example
        return '{"action": "attack", "target": "goblin_01"}'

    def speech_to_text(self, audio_file) -> str:
        """Integration for Whisper API"""
        return "I attack the goblin."

    def text_to_speech(self, text_content: str):
        """Integration for ElevenLabs / OpenAI TTS"""
        print(f"🔊 [TTS PLAYING]: {text_content}")
