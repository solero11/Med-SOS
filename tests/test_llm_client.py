"""
Test harness for LLM Client Module
"""
import unittest
from unittest.mock import patch
from src.llm.llm_client import LLMClient

class TestLLMClient(unittest.TestCase):
    @patch('src.llm.llm_client.requests.post')
    def test_ask_builds_chat_completion_payload(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": "SIGNIFICANT change in rhyme"}}]
        }
        client = LLMClient(
            api_url="http://localhost:1234/v1/chat/completions",
            system_prompt="Always answer in rhymes. Today is Thursday",
            model="medicine-llm-13b",
            temperature=0.7,
            max_tokens=-1,
            stream=False,
        )
        result = client.ask("What day is it today?")
        self.assertEqual(result, "SIGNIFICANT change in rhyme")
        mock_post.assert_called_once()
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["model"], "medicine-llm-13b")
        self.assertEqual(payload["temperature"], 0.7)
        self.assertFalse(payload["stream"])
        self.assertNotIn("max_tokens", payload)
        self.assertEqual(payload["messages"][-1]["content"], "What day is it today?")
        self.assertEqual(payload["messages"][0]["role"], "system")

    @patch('src.llm.llm_client.requests.post')
    def test_ask_includes_context_and_history(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"response": "fallback"}
        client = LLMClient(api_url="http://fake-api", system_prompt="system")
        history = [{"role": "assistant", "content": "Prior response"}]
        context = {"field": "value"}
        client.ask("New input", context=context, history=history)
        payload = mock_post.call_args.kwargs["json"]
        messages = payload["messages"]
        self.assertIn("Context", messages[1]["content"])
        self.assertEqual(messages[2], history[0])
        self.assertEqual(messages[-1]["role"], "user")

if __name__ == "__main__":
    unittest.main()
