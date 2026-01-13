import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import os
import time
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

    @patch('agent_core.completion')
    @patch('agent_core.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_process_message_execution_saves_file(self, mock_file, mock_makedirs, mock_completion):
        # Mocking an executing response
        filename = "spec.md"
        content = "# Specification"
        mock_response_content = json.dumps({
            "status": "executing",
            "content": content,
            "thought_process": "Writing specs",
            "filename": filename
        })

        mock_choice = MagicMock()
        mock_choice.message.content = mock_response_content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response

        history = self.agent.get_initial_history()
        result = self.agent.process_message(history, "Go ahead")

        # Verify parsing
        self.assertEqual(result['parsed']['status'], "executing")
        self.assertEqual(result['parsed']['content'], content)
        self.assertEqual(result['parsed']['filename'], filename)

        # Verify file saving
        expected_path = os.path.join("output", filename)
        self.assertEqual(result['saved_to'], expected_path)

        mock_makedirs.assert_called_with("output")
        mock_file.assert_called_with(expected_path, "w", encoding="utf-8")
        mock_file().write.assert_called_with(content)

    @patch('agent_core.completion')
    @patch('agent_core.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('agent_core.time.time')
    def test_process_message_execution_default_filename(self, mock_time, mock_file, mock_makedirs, mock_completion):
        # Mock time
        mock_time.return_value = 1234567890

        # Mocking an executing response without filename
        content = "print('hello')"
        mock_response_content = json.dumps({
            "status": "executing",
            "content": content,
            "thought_process": "Writing code"
        })

        mock_choice = MagicMock()
        mock_choice.message.content = mock_response_content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response

        history = self.agent.get_initial_history()
        result = self.agent.process_message(history, "Go")

        # Verify filename generation
        expected_filename = "output_1234567890.md"
        expected_path = os.path.join("output", expected_filename)

        self.assertEqual(result['saved_to'], expected_path)
        mock_file.assert_called_with(expected_path, "w", encoding="utf-8")
        mock_file().write.assert_called_with(content)

if __name__ == '__main__':
    unittest.main()
