import unittest
from unittest.mock import patch, MagicMock
import json
from fastapi.testclient import TestClient
from server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch('agent_core.completion')
    def test_chat_endpoint_success(self, mock_completion):
        # Mocking the response
        mock_response_content = json.dumps({
            "status": "interviewing",
            "content": "Hello there!",
            "thought_process": "Greeting user"
        })

        mock_choice = MagicMock()
        mock_choice.message.content = mock_response_content
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_completion.return_value = mock_response

        payload = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": "gpt-4o"
        }

        response = self.client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["parsed"]["status"], "interviewing")
        self.assertEqual(data["parsed"]["content"], "Hello there!")
        self.assertEqual(data["raw"], mock_response_content)

    @patch('agent_core.completion')
    def test_chat_endpoint_error(self, mock_completion):
        # Mocking an exception
        mock_completion.side_effect = Exception("API Down")

        payload = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": "gpt-4o"
        }

        response = self.client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 200) # Agent handles errors and returns JSON
        data = response.json()

        self.assertEqual(data["parsed"]["status"], "error")
        self.assertIn("API Error", data["parsed"]["content"])

if __name__ == '__main__':
    unittest.main()
