import sys
from unittest.mock import MagicMock

# Mock openai module before importing LLMGateway
# This is necessary because the openai package is not installed in the environment
mock_openai_module = MagicMock()
sys.modules['openai'] = mock_openai_module

import unittest
from unittest.mock import patch
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.llm_gateway import LLMGateway

class TestLLMGateway(unittest.TestCase):
    @patch('src.modules.llm_gateway.OpenAI')
    def test_init(self, MockOpenAI):
        gateway = LLMGateway(api_key="test-key")
        MockOpenAI.assert_called_with(api_key="test-key")
        self.assertEqual(gateway.client, MockOpenAI.return_value)

    @patch('src.modules.llm_gateway.OpenAI')
    def test_generate_narrative(self, MockOpenAI):
        # Setup mock
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Generated narrative"
        mock_client.chat.completions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        result = gateway.generate_narrative("System prompt", "User prompt")

        # Assertions
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], "gpt-4o")
        self.assertEqual(call_args.kwargs['messages'], [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "User prompt"}
        ])
        self.assertEqual(result, "Generated narrative")

    @patch('src.modules.llm_gateway.OpenAI')
    def test_generate_json(self, MockOpenAI):
        # Setup mock
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '{"key": "value"}'
        mock_client.chat.completions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        result = gateway.generate_json("User text", "Schema prompt")

        # Assertions
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], "gpt-4o")
        self.assertEqual(call_args.kwargs['response_format'], {"type": "json_object"})

        messages = call_args.kwargs['messages']
        content_combined = " ".join([m['content'] for m in messages])
        self.assertIn("Schema prompt", content_combined)
        self.assertIn("User text", content_combined)

        self.assertEqual(result, '{"key": "value"}')

    @patch('src.modules.llm_gateway.OpenAI')
    def test_speech_to_text(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.text = "Transcribed text"
        mock_client.audio.transcriptions.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        mock_file = MagicMock()
        result = gateway.speech_to_text(mock_file)

        mock_client.audio.transcriptions.create.assert_called_once()
        self.assertEqual(result, "Transcribed text")
        self.assertEqual(mock_client.audio.transcriptions.create.call_args.kwargs['model'], "whisper-1")
        self.assertEqual(mock_client.audio.transcriptions.create.call_args.kwargs['file'], mock_file)

    @patch('src.modules.llm_gateway.OpenAI')
    def test_text_to_speech(self, MockOpenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        # Mock stream_to_file behavior
        mock_response.stream_to_file = MagicMock()
        mock_client.audio.speech.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        gateway.text_to_speech("Hello world")

        mock_client.audio.speech.create.assert_called_once()
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['model'], "tts-1")
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['voice'], "alloy")
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['input'], "Hello world")

        # Verify it attempts to save the file
        mock_response.stream_to_file.assert_called_once()

if __name__ == '__main__':
    unittest.main()
