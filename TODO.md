# Project Roadmap: Intent Extraction Agent

This document outlines the tasks required to transform the current "Second Draft" prototype into a fully shippable, multi-interface application (CLI, REST API, Web UI).

## Phase 1: Core Refactoring (The Brain)
The current implementation mixes User I/O (`input`, `print`) with Agent Logic (`completion`, `json parsing`). We need to separate them.

- [x] **Create `agent_core.py`**
    - [x] Define an `Agent` class.
    - [x] Implement a `process_message(history, user_input)` method that returns the parsed JSON response (`status`, `content`, `thought_process`).
    - [x] Ensure the class is stateless (accepts history) or manages its own state cleanly, allowing for API usage.
    - [x] Move `SYSTEM_PROMPT` and `MODEL_NAME` configuration into this module.

## Phase 2: Persistence
The agent needs to be able to save its "Execution" results to the file system.

- [ ] **Implement Output Handler**
    - [ ] Create a utility function to save content to a file.
    - [ ] In the `executing` state, trigger this save function.
    - [ ] (Optional) Allow user to define filename in the prompt or via configuration.

## Phase 3: Interfaces
Implement the three required entry points using the shared `agent_core`.

- [ ] **CLI Tool (`cli.py`)**
    - [ ] Re-implement the current `while True` loop using the new `Agent` class.
    - [ ] Add argument parsing (using `argparse` or `click`) for custom configuration (e.g., model selection).
    - [ ] Ensure clean colored output (using `rich` or similar) for better UX.

- [ ] **REST API (`server.py`)**
    - [ ] Initialize a **FastAPI** application.
    - [ ] Create an endpoint `POST /chat` that accepts `{ messages: [], model: "..." }`.
    - [ ] Return the structured JSON response from the Agent.
    - [ ] Create an endpoint `GET /health` for connectivity checks.
    - [ ] Add API documentation (Swagger/OpenAPI is built-in with FastAPI).

- [ ] **Web UI (`app.py`)**
    - [ ] Initialize a **Streamlit** or **Gradio** app.
    - [ ] Create a chat interface that maintains session state.
    - [ ] Connect the UI to the `Agent` class (or call the API if preferred, but direct import is simpler for a mono-repo).
    - [ ] Display "Thought Process" and "Content" in distinct UI elements.

## Phase 4: DevOps & Deployment
Make the application "shippable" and "deployable".

- [ ] **Dependency Management**
    - [ ] Create a `requirements.txt` with locked versions (litellm, fastapi, uvicorn, streamlit, python-dotenv, etc.).

- [ ] **Dockerization**
    - [ ] Create a `Dockerfile`.
    - [ ] Configure it to expose necessary ports (e.g., 8000 for API, 8501 for Streamlit).
    - [ ] Create a `docker-compose.yml` to run the API and UI services simultaneously (optional but recommended).

## Phase 5: Testing & Quality
- [ ] **Unit Tests**
    - [ ] Test `agent_core` logic (mocking the LLM call) to ensure it correctly parses JSON and handles states.
- [ ] **Integration Tests**
    - [ ] Test the API endpoints.
