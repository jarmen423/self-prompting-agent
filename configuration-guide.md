Both Kilo Code (the app/gateway) and OpenCode (specifically the "Zen" cloud service) typically function as OpenAI-Compatible endpoints. This means they speak the same language as OpenAI, but you just need to point LiteLLM to their "house" instead of OpenAI's.

Here is how to configure them.

1. The Universal "Skeleton Key" Configuration
For almost any "Access Gateway" or "All-in-One" key (like OpenCode Zen, Kilo, or local tools like LM Studio), you use the openai/ prefix but change the Base URL.

In your Python script:

```python
# The prefix is ALWAYS 'openai/' because they speak the OpenAI language.
# The Model Name is whatever specific model they support (e.g., "claude-3-5-sonnet")
MODEL_NAME = "openai/claude-3-5-sonnet"
```

In your `.env` file:
```bash
# 1. The Key you got from them
OPENAI_API_KEY=kc-12345-your-kilo-or-opencode-key

# 2. The Address (This is the critical part!)
# You must find the "Base URL" in their docs.
OPENAI_API_BASE=https://api.opencode.ai/v1
```

2. Specific Configs for Your Tools
For OpenCode (Zen)
If you are using the OpenCode Zen cloud service (where you pay them directly and get one key for everything), they act as a proxy.

Provider Prefix: openai/

Env Variable: OPENAI_API_BASE=https://api.opencode.ai/v1 (Check their specific endpoint in your dashboard, sometimes it is https://gateway.opencode.ai/v1).

Why? OpenCode Zen wraps other models (Claude, GPT, etc.) in an OpenAI-style package.

For Kilo (Kilo Code)
Kilo Code is often a client (like VS Code), but if you are using their Gateway or Cloud Sync key:

Provider Prefix: openai/

Env Variable: OPENAI_API_BASE -> You need to copy the endpoint URL they give you in the Kilo settings (often under "Server URL" or "Gateway Address").


3. The "Gotcha": Conflicting Keys
If you try to use OPENAI_API_KEY for both real OpenAI and OpenCode in the same script, they will clash.

The Fix: Use LiteLLM's specific naming convention to keep them separate.

Updated .env:

```bash
# Real OpenAI
OPENAI_API_KEY=sk-proj-123...

# OpenCode (Use a custom name)
OPENCODE_API_KEY=zk-123...
OPENCODE_API_BASE=https://api.opencode.ai/v1
```

In your Python script:

```python
# Tell LiteLLM exactly where to look for the OpenCode params
response = completion(
    model="openai/claude-3-5-sonnet", # Still says "openai/"
    api_key=os.getenv("OPENCODE_API_KEY"),     # Manually grab the specialized key
    base_url=os.getenv("OPENCODE_API_BASE")    # Manually grab the specialized URL
)
```

