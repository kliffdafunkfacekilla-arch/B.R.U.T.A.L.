from openai import OpenAI
import os
# This is a stub. In production, use 'openai' or 'google-generativeai' libraries.
import google.generativeai as genai
import os
import json
import os
from openai import OpenAI

class LLMGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # If api_key is "dummy_key", we might want to default to environment variable
        # or handle it gracefully. For now, we trust the caller.
        self.client = OpenAI(api_key=self.api_key)
        if self.api_key != "dummy_key":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key)

    async def generate_narrative(self, system_prompt: str, user_prompt: str) -> str:
        """
        Used for the Storyteller / Micro-Generator.
        Returns pure text for the TTS to read.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Cost-effective default
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
        # Call GPT-4 / Gemini Pro here
        # response = await client.chat.completions.create(...)
        print(f"\n[AI THOUGHTS]: Processing Narrative...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
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
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in generate_narrative: {e}")
            # Fallback for dev/test without key
            return "Simulated Narrative: The goblin shrieks as your sword connects!"

    async def generate_json(self, user_text: str, schema_prompt: str) -> str:
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
        print(f"\n[AI THOUGHTS]: Parsing Intent...")
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant designed to output JSON. {schema_prompt}"},
                    {"role": "user", "content": user_text}
                ]
            )
            return response.choices[0].message.content
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
