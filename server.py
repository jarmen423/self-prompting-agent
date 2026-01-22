from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from agent_core import Agent, MODEL_NAME

app = FastAPI(title="Intent Extraction Agent API")

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = MODEL_NAME

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Process a chat message using the Agent.
    Accepts a list of messages (history) and an optional model name.
    Returns the agent's structured response.
    """
    try:
        # Initialize agent with the requested model
        agent = Agent(model_name=request.model)

        # Process the message.
        # We pass the entire message history from the client.
        # user_input is None because the last message in 'messages' is assumed to be the user's input
        # or the client is managing history fully.
        response = agent.process_message(history=request.messages)

        return response
    except Exception as e:
        # Fallback for unexpected errors not caught by agent_core
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
