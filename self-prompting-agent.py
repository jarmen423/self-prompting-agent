import os
import json
from litellm import completion
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

# <--- CONFIGURATION --->
# You can swap this string for "claude-3-opus-20240229", "ollama/llama3", etc.
MODEL_NAME = "gpt-4o"

# This is the "Brain" prompt we will refine later.
# It MUST instruct the model to return JSON.
SYSTEM_PROMPT = """
You are an Expert Requirements Engineer. Your goal is to extract intent.

PROTOCOL:
1. If the user request is vague, ask clarifying questions.
2. If the user request is clear, summarize it and ask for verification.
3. ONLY when the user says "Yes" or "Correct", generate the final output.

OUTPUT FORMAT:
You must ALWAYS respond with a JSON object in this exact format:
{
    "status": "interviewing" | "verifying" | "executing",
    "message": "Your response to the user here...",
    "final_output": null | "The actual code/essay/result goes here if status is executing"
}
"""

def run_agent_loop():
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    print(f"--- Agent Initialized ({MODEL_NAME}) ---")
    print("Agent: How can I help you today?")

    turn_count = 0
    max_turns = 10  # Safety break

    while turn_count < max_turns:
        # 1. Get User Input
        user_input = input("You: ")
        messages.append({"role": "user", "content": user_input})

        # 2. Call the Model (The "Worker")
        try:
            response = completion(
                model=MODEL_NAME,
                messages=messages,
                response_format={"type": "json_object"} # Forces valid JSON
            )

            # Extract content
            ai_content = response.choices[0].message.content

            # 3. Parse the Logic (The "Manager")
            data = json.loads(ai_content)
            status = data.get("status")
            message = data.get("message")
            final_output = data.get("final_output")

            # Update history so the model remembers the context
            messages.append({"role": "assistant", "content": ai_content})

            # 4. Handle States
            if status == "interviewing":
                print(f"\nAgent (Clarifying): {message}")

            elif status == "verifying":
                print(f"\nAgent (Verifying): {message}")

            elif status == "executing":
                print(f"\nAgent (Executing): {message}")
                print("-" * 20)
                print("FINAL OUTPUT:")
                print(final_output)
                break # <--- EXIT LOOP

            else:
                print(f"\nError: Unknown status '{status}'. logic failed.")

        except Exception as e:
            print(f"Error calling LLM: {e}")
            break

        turn_count += 1

if __name__ == "__main__":
    run_agent_loop()
