import unittest
from unittest.mock import patch, MagicMock
import json
from agent_core import Agent, SYSTEM_PROMPT, MODEL_NAME

class TestAgentCore(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()

    def test_initialization(self):
        self.assertEqual(self.agent.model_name, MODEL_NAME)
        self.assertEqual(self.agent.system_prompt, SYSTEM_PROMPT)

    def test_get_initial_history(self):
        history = self.agent.get_initial_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['role'], 'system')
        self.assertEqual(history[0]['content'], SYSTEM_PROMPT)

    @patch('agent_core.completion')
    def test_process_message_success(self, mock_completion):
        # Mocking the response
        mock_response_content = json.dumps({
            "status": "interviewing",
            "content": "What is your goal?",
            "thought_process": "Need more info"
        })

        mock_choice = MagicMock()
        mock_choice.message.content = mock_response_content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response

        history = self.agent.get_initial_history()
        user_input = "I want to build a bot."

        result = self.agent.process_message(history, user_input)

        # Verify litellm call
        expected_messages = history + [{"role": "user", "content": user_input}]
        mock_completion.assert_called_once_with(
            model=MODEL_NAME,
            messages=expected_messages,
            response_format={"type": "json_object"}
        )

        # Verify result
        self.assertEqual(result['parsed']['status'], "interviewing")
        self.assertEqual(result['parsed']['content'], "What is your goal?")
        self.assertEqual(result['parsed']['thought_process'], "Need more info")
        self.assertEqual(result['raw'], mock_response_content)

    @patch('agent_core.completion')
    def test_process_message_json_error(self, mock_completion):
        # Mocking a bad JSON response
        bad_json = "This is not JSON."

        mock_choice = MagicMock()
        mock_choice.message.content = bad_json
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response

        history = self.agent.get_initial_history()
        result = self.agent.process_message(history, "Hello")

        self.assertEqual(result['parsed']['status'], "error")
        self.assertIn("Model failed to return JSON", result['parsed']['content'])
        self.assertEqual(result['raw'], bad_json)

    @patch('agent_core.completion')
    def test_process_message_api_error(self, mock_completion):
        # Mocking an exception
        mock_completion.side_effect = Exception("API Connection Failed")

        history = self.agent.get_initial_history()
        result = self.agent.process_message(history, "Hello")

        self.assertEqual(result['parsed']['status'], "error")
        self.assertIn("API Error: API Connection Failed", result['parsed']['content'])
        self.assertEqual(result['raw'], "")

if __name__ == '__main__':
    unittest.main()
