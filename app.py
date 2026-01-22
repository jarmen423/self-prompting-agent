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

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.agent.get_initial_history()

# Initialize Latest Thought Process
if "latest_thought" not in st.session_state:
    st.session_state.latest_thought = "Waiting for agent activity..."

# Sidebar for Thought Process - Using placeholder
with st.sidebar:
    st.header("🧠 Thought Process")
    thought_placeholder = st.empty()
    thought_placeholder.info(st.session_state.latest_thought)

# Display Chat Messages (excluding system prompt)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("What would you like to build?"):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process message with spinner
    with st.spinner("Thinking..."):
        response_data = st.session_state.agent.process_message(st.session_state.messages, prompt)

    # Update state
    st.session_state.messages.append({"role": "user", "content": prompt})

    parsed = response_data["parsed"]
    ai_content = parsed.get("content", "")
    thought_process = parsed.get("thought_process", "")
    status = parsed.get("status", "unknown")

    st.session_state.messages.append({"role": "assistant", "content": ai_content})

    # Update thought process
    if thought_process:
        st.session_state.latest_thought = thought_process
        # Update the placeholder immediately
        thought_placeholder.info(thought_process)

    # Display AI response
    with st.chat_message("assistant"):
        st.markdown(ai_content)

    # Check for file saving
    if status == "executing" and response_data.get("saved_to"):
        st.success(f"✅ File saved to: `{response_data['saved_to']}`")
