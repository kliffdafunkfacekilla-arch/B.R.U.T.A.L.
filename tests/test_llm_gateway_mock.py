import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.llm_gateway import LLMGateway

class TestLLMGateway(unittest.IsolatedAsyncioTestCase):

    @patch('src.modules.llm_gateway.OpenAI')
    @patch.dict(os.environ, {}, clear=True)
    def test_init(self, MockOpenAI):
        # We expect OpenAI to be called twice: once for Ollama, once for Audio
        gateway = LLMGateway(api_key="test-key")

        # Check calls
        self.assertEqual(MockOpenAI.call_count, 2)

        # First call (Ollama)
        call_args_1 = MockOpenAI.call_args_list[0]
        self.assertEqual(call_args_1.kwargs['base_url'], "http://localhost:11434/v1")
        self.assertEqual(call_args_1.kwargs['api_key'], "ollama")

        # Second call (Audio)
        call_args_2 = MockOpenAI.call_args_list[1]
        self.assertEqual(call_args_2.kwargs['api_key'], "test-key")

    @patch('src.modules.llm_gateway.OpenAI')
    async def test_generate_narrative(self, MockOpenAI):
        # Setup mocks
        mock_llm_client = MagicMock()
        mock_audio_client = MagicMock()

        # Configure the side_effect to return distinct mocks for the two calls
        MockOpenAI.side_effect = [mock_llm_client, mock_audio_client]

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated narrative"
        mock_llm_client.chat.completions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        result = await gateway.generate_narrative("System prompt", "User prompt")

        # Assertions
        mock_llm_client.chat.completions.create.assert_called_once()
        call_args = mock_llm_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], "llama3:latest")
        self.assertEqual(call_args.kwargs['messages'], [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"}
        ])
        self.assertEqual(result, "Generated narrative")

    @patch('src.modules.llm_gateway.OpenAI')
    async def test_generate_json(self, MockOpenAI):
        # Setup mocks
        mock_llm_client = MagicMock()
        mock_audio_client = MagicMock()
        MockOpenAI.side_effect = [mock_llm_client, mock_audio_client]

        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_llm_client.chat.completions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        result = await gateway.generate_json("User text", "Schema prompt")

        # Assertions
        mock_llm_client.chat.completions.create.assert_called_once()
        call_args = mock_llm_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], "qwen2.5:latest")
        self.assertEqual(call_args.kwargs['response_format'], {"type": "json_object"})

        messages = call_args.kwargs['messages']
        content_combined = " ".join([m['content'] for m in messages])
        self.assertIn("Schema prompt", content_combined)
        self.assertIn("User text", content_combined)

        self.assertEqual(result, '{"key": "value"}')

    @patch('src.modules.llm_gateway.OpenAI')
    def test_speech_to_text(self, MockOpenAI):
        # Setup mocks
        mock_llm_client = MagicMock()
        mock_audio_client = MagicMock()
        MockOpenAI.side_effect = [mock_llm_client, mock_audio_client]

        mock_response = MagicMock()
        mock_response.text = "Transcribed text"
        mock_audio_client.audio.transcriptions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        mock_file = MagicMock()
        result = gateway.speech_to_text(mock_file)

        mock_audio_client.audio.transcriptions.create.assert_called_once()
        self.assertEqual(result, "Transcribed text")
        self.assertEqual(mock_audio_client.audio.transcriptions.create.call_args.kwargs['model'], "whisper-1")
        self.assertEqual(mock_audio_client.audio.transcriptions.create.call_args.kwargs['file'], mock_file)

    @patch('src.modules.llm_gateway.OpenAI')
    def test_text_to_speech(self, MockOpenAI):
        # Setup mocks
        mock_llm_client = MagicMock()
        mock_audio_client = MagicMock()
        MockOpenAI.side_effect = [mock_llm_client, mock_audio_client]

        mock_response = MagicMock()
        mock_response.stream_to_file = MagicMock()
        mock_audio_client.audio.speech.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        gateway.text_to_speech("Hello world")

        mock_audio_client.audio.speech.create.assert_called_once()
        self.assertEqual(mock_audio_client.audio.speech.create.call_args.kwargs['model'], "tts-1")
        self.assertEqual(mock_audio_client.audio.speech.create.call_args.kwargs['voice'], "alloy")
        self.assertEqual(mock_audio_client.audio.speech.create.call_args.kwargs['input'], "Hello world")

if __name__ == '__main__':
    unittest.main()
