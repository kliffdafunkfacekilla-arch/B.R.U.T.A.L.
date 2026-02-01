import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.llm_gateway import LLMGateway

class TestLLMGateway(unittest.IsolatedAsyncioTestCase):

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    @patch.dict(os.environ, {"OPENAI_API_KEY": "env-openai-key"}, clear=True)
    def test_init_with_env_key(self, MockOpenAI, MockGenAI):
        gateway = LLMGateway(api_key="gemini-key")
        MockGenAI.configure.assert_called_with(api_key="gemini-key")
        MockOpenAI.assert_called_with(api_key="env-openai-key")
        self.assertEqual(gateway.client, MockOpenAI.return_value)

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_env_key(self, MockOpenAI, MockGenAI):
        gateway = LLMGateway(api_key="gemini-key")
        MockGenAI.configure.assert_called_with(api_key="gemini-key")
        # Assert it uses the fallback
        MockOpenAI.assert_called_with(api_key="missing_openai_key")

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    async def test_generate_narrative(self, MockOpenAI, MockGenAI):
        # Setup mock for Gemini
        mock_model = MagicMock()
        MockGenAI.GenerativeModel.return_value = mock_model

        mock_response = MagicMock()
        mock_response.text = "Generated narrative"

        # AsyncMock for the async method
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        gateway = LLMGateway(api_key="test-key")
        result = await gateway.generate_narrative("System prompt", "User prompt")

        # Assertions
        MockGenAI.GenerativeModel.assert_called_with("gemini-1.5-flash", system_instruction="System prompt")
        mock_model.generate_content_async.assert_called_with("User prompt")
        self.assertEqual(result, "Generated narrative")

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    async def test_generate_json(self, MockOpenAI, MockGenAI):
        # Setup mock for Gemini
        mock_model = MagicMock()
        MockGenAI.GenerativeModel.return_value = mock_model

        mock_response = MagicMock()
        mock_response.text = '{"key": "value"}'

        # AsyncMock
        mock_model.generate_content_async = AsyncMock(return_value=mock_response)

        gateway = LLMGateway(api_key="test-key")
        result = await gateway.generate_json("User text", "Schema prompt")

        # Assertions
        MockGenAI.GenerativeModel.assert_called_with(
            "gemini-1.5-flash",
            system_instruction="You are a helpful assistant designed to output JSON. Schema prompt",
            generation_config={"response_mime_type": "application/json"}
        )

        mock_model.generate_content_async.assert_called_with("User text")
        self.assertEqual(result, '{"key": "value"}')

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    def test_speech_to_text(self, MockOpenAI, MockGenAI):
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

    @patch('src.modules.llm_gateway.genai')
    @patch('src.modules.llm_gateway.OpenAI')
    def test_text_to_speech(self, MockOpenAI, MockGenAI):
        mock_client = MockOpenAI.return_value
        mock_response = MagicMock()
        mock_response.stream_to_file = MagicMock()
        mock_client.audio.speech.create.return_value = mock_response

        gateway = LLMGateway(api_key="test-key")
        gateway.text_to_speech("Hello world")

        mock_client.audio.speech.create.assert_called_once()
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['model'], "tts-1")
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['voice'], "alloy")
        self.assertEqual(mock_client.audio.speech.create.call_args.kwargs['input'], "Hello world")

if __name__ == '__main__':
    unittest.main()
