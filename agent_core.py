import json
import os
import time
from litellm import completion
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# <--- CONFIGURATION --->
MODEL_NAME = "openai/gpt-4o"

# <--- THE BRAIN: SYSTEM PROMPT --->
SYSTEM_PROMPT = """
### ROLE
You are an Expert Requirements Engineer and Architect.
Your GOAL is to extract a crystal-clear "Specification" from the user before any work begins.

### PROTOCOL (THE LOOP)
1.  **ANALYSIS**: When the user sends a message, analyze it. Is it a vague idea or a complete technical spec?
2.  **INTERVIEW**: If vague, ask 3-5 distinct, high-impact questions to clarify constraints, tech stack, and user goals.
    * *Do not* just say "tell me more." Ask specific things like "Do you prefer Python or Node?" or "Is this for mobile or web?"
3.  **VERIFICATION**: Once you have enough info, generate a "Vision Summary" and ask the user to confirm it.
4.  **EXECUTION**: ONLY when the user explicitly says "Yes", "Confirmed", or "Proceed", shift to the execution phase.

### OUTPUT FORMAT (MANDATORY)
You must ALWAYS respond with valid JSON in this structure:
{
    "status": "interviewing" | "verifying" | "executing",
    "thought_process": "Briefly explain why you are in this state...",
    "content": "The actual text you want to show the user (questions, summary, or final code)...",
    "filename": "(Optional) Suggested filename for the content if status is executing (e.g., 'spec.md', 'code.py')"
}
"""

class Agent:
    def __init__(self, model_name=MODEL_NAME, system_prompt=SYSTEM_PROMPT):
        self.model_name = model_name
        self.system_prompt = system_prompt

    def get_initial_history(self):
        """Returns the initial history with the system prompt."""
        return [{"role": "system", "content": self.system_prompt}]

    def save_to_file(self, content, filename=None):
        """
        Saves content to a file in the 'output' directory.

        Args:
            content (str): The text content to save.
            filename (str, optional): The filename. If None, generates a timestamped name.

        Returns:
            str: The full path to the saved file.
        """
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not filename:
            timestamp = int(time.time())
            filename = f"output_{timestamp}.md"

        # Sanitize filename to prevent directory traversal (basic check)
        filename = os.path.basename(filename)

        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        return filepath

    def process_message(self, history, user_input=None):
        """
        Process a user message and return the agent's response.

        Args:
            history (list): List of message dictionaries (role, content).
            user_input (str, optional): The new user message to append.

        Returns:
            dict: Parsed JSON response from the agent plus the raw response content.
                  Structure:
                  {
                      "parsed": { "status": "...", "content": "...", "thought_process": "...", "filename": "..." },
                      "raw": "...",
                      "saved_to": "path/to/file" (if applicable)
                  }
        """
        # Create a copy of messages to send to the LLM
        messages = list(history)

        if user_input:
            messages.append({"role": "user", "content": user_input})

        try:
            response = completion(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"} # Force JSON reliability
            )

            ai_raw = response.choices[0].message.content
            saved_path = None

            try:
                data = json.loads(ai_raw)
                # Ensure default keys if missing
                status = data.get("status", "interviewing")
                content = data.get("content", "")
                thought_process = data.get("thought_process", "")
                filename = data.get("filename")

                if status == "executing" and content:
                    saved_path = self.save_to_file(content, filename)

                return {
                    "parsed": {
                        "status": status,
                        "content": content,
                        "thought_process": thought_process,
                        "filename": filename
                    },
                    "raw": ai_raw,
                    "saved_to": saved_path
                }

            except json.JSONDecodeError:
                return {
                    "parsed": {
                        "status": "error",
                        "content": f"Model failed to return JSON. Raw output:\n{ai_raw}",
                        "thought_process": "JSON Parsing Error"
                    },
                    "raw": ai_raw
                }

        except Exception as e:
            error_msg = str(e)
            return {
                "parsed": {
                    "status": "error",
                    "content": f"API Error: {error_msg}",
                    "thought_process": "API Call Error"
                },
                "raw": ""
            }
