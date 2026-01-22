import streamlit as st
import os
from agent_core import Agent

# Set page configuration
st.set_page_config(
    page_title="Intent Extraction Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Intent Extraction Agent")

# Initialize Agent
if "agent" not in st.session_state:
    st.session_state.agent = Agent()

# Initialize Chat History for LLM (includes system prompt and raw JSON responses)
if "llm_history" not in st.session_state:
    st.session_state.llm_history = st.session_state.agent.get_initial_history()

# Initialize Chat History for Display (parsed content only, no system prompt)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Latest Thought Process
if "latest_thought" not in st.session_state:
    st.session_state.latest_thought = "Waiting for agent activity..."

# Initialize Latest File (for persistent download)
if "latest_file" not in st.session_state:
    st.session_state.latest_file = None

# Sidebar
with st.sidebar:
    st.header("🧠 Thought Process")
    thought_placeholder = st.empty()
    thought_placeholder.info(st.session_state.latest_thought)

    st.divider()

    st.header("📂 Output")
    download_placeholder = st.empty()

    # Render persistent download button if exists
    if st.session_state.latest_file and os.path.exists(st.session_state.latest_file):
        filepath = st.session_state.latest_file
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
            filename = os.path.basename(filepath)
            download_placeholder.download_button(
                label=f"Download {filename}",
                data=file_content,
                file_name=filename,
                mime="text/markdown",
                key="persistent_download"
            )
        except Exception:
            pass # Ignore read errors during initial render

# Display Chat Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What would you like to build?"):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process message with spinner
    with st.spinner("Thinking..."):
        # We pass the LLM history and the new prompt
        response_data = st.session_state.agent.process_message(st.session_state.llm_history, prompt)

    # Update LLM History
    st.session_state.llm_history.append({"role": "user", "content": prompt})
    st.session_state.llm_history.append({"role": "assistant", "content": response_data["raw"]})

    # Update Display History
    st.session_state.messages.append({"role": "user", "content": prompt})

    parsed = response_data["parsed"]
    ai_content = parsed.get("content", "")
    thought_process = parsed.get("thought_process", "")
    status = parsed.get("status", "unknown")

    st.session_state.messages.append({"role": "assistant", "content": ai_content})

    # Update thought process
    if thought_process:
        st.session_state.latest_thought = thought_process
        thought_placeholder.info(thought_process)

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_content)

    # Check for file saving
    if status == "executing" and response_data.get("saved_to"):
        filepath = response_data['saved_to']
        st.session_state.latest_file = filepath
        st.success(f"✅ File saved to: `{filepath}`")

        # Update download button immediately
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
            filename = os.path.basename(filepath)
            download_placeholder.download_button(
                label=f"Download {filename}",
                data=file_content,
                file_name=filename,
                mime="text/markdown",
                key="immediate_download"
            )
        except Exception as e:
            st.error(f"Could not prepare download: {e}")
