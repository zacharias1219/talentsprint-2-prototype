"""
Main Streamlit application.

AI-Powered Financial Advisor chat interface.
"""

import streamlit as st
from src.api.routes import APIRoutes
from src.compliance.compliance_checker import ComplianceChecker
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💰",
    layout="wide",
)

# Initialize components
if "api_routes" not in st.session_state:
    st.session_state.api_routes = APIRoutes()

if "compliance_checker" not in st.session_state:
    st.session_state.compliance_checker = ComplianceChecker()

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def main():
    """Main application function."""
    st.title("💰 AI-Powered Financial Advisor")

    # Sidebar for user profile
    with st.sidebar:
        st.header("User Profile")
        user_id = st.text_input("User ID", value=st.session_state.user_id or "")
        if user_id:
            st.session_state.user_id = user_id

        if st.button("Create Profile"):
            st.info("Profile creation form would go here")

    # Main chat interface
    st.header("Chat with your Financial Advisor")

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about your finances..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate response
        with st.chat_message("assistant"):
            if st.session_state.user_id:
                response = st.session_state.api_routes.chat_message(
                    st.session_state.user_id,
                    prompt,
                )
                response_text = response.get("response_text", "I apologize, but I couldn't generate a response.")

                # Add disclaimers
                response_text = st.session_state.compliance_checker.add_disclaimers(response_text)

                st.markdown(response_text)

                # Show sources if available
                sources = response.get("sources", [])
                if sources:
                    with st.expander("Sources"):
                        for source in sources[:3]:  # Show top 3 sources
                            st.write(f"- {source.get('text', '')[:100]}...")
            else:
                st.warning("Please enter a User ID in the sidebar to start chatting.")

            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text if st.session_state.user_id else "Please enter a User ID.",
            })


if __name__ == "__main__":
    main()

