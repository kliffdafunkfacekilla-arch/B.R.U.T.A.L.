from openai import OpenAI
import os

class LLMGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # If api_key is "dummy_key", we might want to default to environment variable
        # or handle it gracefully. For now, we trust the caller.
        self.client = OpenAI(api_key=self.api_key)

    def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """
        Used for the Storyteller / Micro-Generator.
        Returns pure text for the TTS to read.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Cost-effective default
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            content = response.choices[0].message.content
            print(f"\n[AI THOUGHTS]: Processing Narrative...")
            return content if content else ""
        except Exception as e:
            print(f"Error generating narrative: {e}")
            return "The mists of uncertainty cloud the vision. (AI Error)"

    def generate_json(self, user_text: str, schema_prompt: str) -> str:
        """
        Used for the Intent Parser and Macro-Generator.
        Forces the model to output valid JSON.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": schema_prompt},
                    {"role": "user", "content": user_text}
                ],
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            print(f"\n[AI THOUGHTS]: Parsing Intent...")
            return content if content else "{}"
        except Exception as e:
            print(f"Error generating JSON: {e}")
            return '{"action": "meta", "content": "AI Error"}'

    def speech_to_text(self, audio_file) -> str:
        """Integration for Whisper API"""
        # Placeholder: Implementing this would require handling file uploads/paths
        raise NotImplementedError("Speech to text not yet implemented.")

    def text_to_speech(self, text_content: str):
        """Integration for ElevenLabs / OpenAI TTS"""
        print(f"🔊 [TTS PLAYING]: {text_content}")
