import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

# Change this to "zai/glm-4" or "minimax/abab6.5-chat" to test specific keys
TEST_MODEL = "openai/MiniMax-M2.1" 

try:
    print(f"Testing connection to {TEST_MODEL}...")
    response = completion(
        model=TEST_MODEL,
        messages=[{"role": "user", "content": "Hello, are you online?"}]
    )
    print("SUCCESS! Response received:")
    print(response.choices[0].message.content)
except Exception as e:
    print("\nCONNECTION FAILED.")
    print("Error details:", e)
    print("\nTROUBLESHOOTING:")
    print("1. Check if your Key matches the Region (China vs Intl).")
    print("2. Check if ZAI_API_BASE includes '/coding/' if using a Coding Plan.")