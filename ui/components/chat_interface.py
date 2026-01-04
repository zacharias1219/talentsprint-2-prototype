"""
Chat interface component for Streamlit.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import json


def render_chat_message(message: Dict[str, Any], show_context: bool = False) -> None:
    """
    Render a chat message with optional context display.

    Args:
        message: Message dictionary with 'role', 'content', and optionally 'context', 'metadata'.
        show_context: Whether to show context in expandable section.
    """
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show context if available
        if show_context and message.get("context"):
            with st.expander("📊 Context Used"):
                st.json(message["context"])
        
        # Show metadata if available
        if message.get("metadata"):
            metadata = message["metadata"]
            with st.expander("ℹ️ Model Info"):
                if metadata.get("model"):
                    st.caption(f"Model: {metadata['model']}")
                if metadata.get("temperature"):
                    st.caption(f"Temperature: {metadata['temperature']}")
                if metadata.get("max_length"):
                    st.caption(f"Max Length: {metadata['max_length']}")


def render_chat_history(messages: List[Dict[str, Any]], show_context: bool = False) -> None:
    """
    Render chat history.

    Args:
        messages: List of message dictionaries.
        show_context: Whether to show context for assistant messages.
    """
    for message in messages:
        render_chat_message(message, show_context=show_context and message["role"] == "assistant")


def render_typing_indicator() -> None:
    """
    Render a typing indicator to show the model is generating.
    """
    with st.chat_message("assistant"):
        st.markdown("💭 *Thinking...*")
        st.spinner("Generating response...")


def render_context_snippet(context_data: Dict[str, Any]) -> None:
    """
    Render a formatted context snippet showing user profile and market data.

    Args:
        context_data: Dictionary containing user context and market data.
    """
    if "user_context" in context_data:
        st.subheader("👤 Your Profile")
        user_ctx = context_data["user_context"]
        if "risk_profile" in user_ctx:
            st.metric("Risk Profile", user_ctx["risk_profile"].get("label", "Unknown"))
        if "target_allocation" in user_ctx:
            st.json(user_ctx["target_allocation"])
    
    if "market_context" in context_data:
        st.subheader("📈 Market Data")
        market_ctx = context_data["market_context"]
        if isinstance(market_ctx, dict):
            st.json(market_ctx)

