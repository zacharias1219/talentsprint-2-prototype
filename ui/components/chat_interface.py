"""
Chat interface component for Streamlit.
"""

import streamlit as st
from typing import Dict, List, Any


def render_chat_message(message: Dict[str, Any]) -> None:
    """
    Render a chat message.

    Args:
        message: Message dictionary with 'role' and 'content'.
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """
    Render chat history.

    Args:
        messages: List of message dictionaries.
    """
    for message in messages:
        render_chat_message(message)

