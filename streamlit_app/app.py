import os
import sys
from pathlib import Path
import streamlit as st
from typing import List

# Add the project root directory to Python path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Import the service from FastAPI app
from app.services.chatbot_service import ChatbotService

# Initialize session state for chat history if it doesn't exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = ChatbotService()

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 AI Chatbot")

# Chat interface
st.markdown("### Chat")

# Display chat history
for message in st.session_state.chat_history:
    role = "user" if message.startswith("Human: ") else "assistant"
    content = message.replace("Human: ", "").replace("AI Assistant: ", "")
    
    with st.chat_message(role):
        st.write(content)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.chat_history.append(f"Human: {prompt}")
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Note: removed await since we modified the service to be synchronous
            response = st.session_state.chatbot.generate_response(
                prompt, 
                st.session_state.chat_history
            )
            st.write(response)
    
    # Add bot response to chat history
    st.session_state.chat_history.append(f"AI Assistant: {response}")

# Sidebar
with st.sidebar:
    st.markdown("### About")
    st.markdown("""
    This is an AI Chatbot powered by Google's Gemini model.
    
    The chatbot can:
    - Engage in natural conversations
    - Remember context from previous messages
    - Provide helpful and creative responses
    """)
    
    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
