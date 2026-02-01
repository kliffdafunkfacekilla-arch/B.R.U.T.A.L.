import os
from openai import OpenAI
import google.generativeai as genai

class LLMGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key

        # Configure Gemini
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            print(f"Error configuring Gemini: {e}")

        # Initialize OpenAI client
        # We rely on OPENAI_API_KEY env var, or fallback to a dummy key.
        # We do NOT use the passed api_key as it is intended for Gemini (per server.py).
        openai_key = os.getenv("OPENAI_API_KEY", "missing_openai_key")
        self.client = OpenAI(api_key=openai_key)

    async def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """
        Used for the Storyteller / Micro-Generator.
        Returns pure text for the TTS to read.
        """
        print(f"\n[AI THOUGHTS]: Processing Narrative...")
        try:
            # Initialize model with system instruction
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=system_prompt
            )

            response = await model.generate_content_async(user_prompt)
            return response.text
        except Exception as e:
            print(f"Error in generate_narrative: {e}")
            # Fallback for dev/test without key
            return "Simulated Narrative: The goblin shrieks as your sword connects!"

    async def generate_json(self, user_text: str, schema_prompt: str) -> str:
        """
        Used for the Intent Parser and Macro-Generator.
        Forces the model to output valid JSON.
        """
        print(f"\n[AI THOUGHTS]: Parsing Intent...")
        try:
            # Initialize model with JSON mode and system instruction
            model = genai.GenerativeModel(
                "gemini-1.5-flash",
                system_instruction=f"You are a helpful assistant designed to output JSON. {schema_prompt}",
                generation_config={"response_mime_type": "application/json"}
            )

            response = await model.generate_content_async(user_text)
            return response.text
        except Exception as e:
            print(f"Error in generate_json: {e}")
            return '{"action": "attack", "target": "goblin_01"}'

    def speech_to_text(self, audio_file) -> str:
        """Integration for Whisper API"""
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            return response.text
        except Exception as e:
            print(f"Error in speech_to_text: {e}")
            return "I attack the goblin."

    def text_to_speech(self, text_content: str):
        """Integration for ElevenLabs / OpenAI TTS"""
        print(f"🔊 [TTS GENERATING]: {text_content}")
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text_content
            )
            output_path = "output_tts.mp3"
            response.stream_to_file(output_path)
            print(f"🔊 [TTS SAVED]: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error in text_to_speech: {e}")
            print(f"🔊 [TTS PLAYING (SIMULATED)]: {text_content}")
