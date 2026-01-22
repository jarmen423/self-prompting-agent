import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @patch('server.Agent')
    def test_chat_endpoint_success(self, MockAgent):
        # Mock the agent instance and its process_message method
        mock_agent_instance = MockAgent.return_value
        mock_response = {
            "parsed": {
                "status": "interviewing",
                "content": "Hello",
                "thought_process": "Greeting",
                "filename": None
            },
            "raw": "...",
            "saved_to": None
        }
        mock_agent_instance.process_message.return_value = mock_response

        # Payload
        payload = {
            "messages": [{"role": "user", "content": "Hi"}],
            "model": "gpt-4-test"
        }

        response = self.client.post("/chat", json=payload)

        # Verify response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_response)

        # Verify Agent was initialized with correct model
        MockAgent.assert_called_with(model_name="gpt-4-test")

        # Verify process_message was called with history
        mock_agent_instance.process_message.assert_called_with(history=payload["messages"])

    @patch('server.Agent')
    def test_chat_endpoint_error(self, MockAgent):
        # Mock an exception
        mock_agent_instance = MockAgent.return_value
        mock_agent_instance.process_message.side_effect = Exception("Internal Error")

        payload = {
            "messages": [{"role": "user", "content": "Hi"}]
        }

        response = self.client.post("/chat", json=payload)

        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal Error", response.json()["detail"])
