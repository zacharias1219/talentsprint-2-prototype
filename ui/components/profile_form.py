"""
User profile form component for Streamlit.
"""

import streamlit as st
from typing import Dict, Any


def render_profile_form() -> Dict[str, Any]:
    """
    Render user profile form.

    Returns:
        Profile data dictionary.
    """
    st.header("Create Your Profile")

    with st.form("profile_form"):
        # Demographics
        st.subheader("Demographics")
        age = st.number_input("Age", min_value=18, max_value=100, value=30)
        income = st.number_input("Annual Income ($)", min_value=0, value=50000)
        employment_status = st.selectbox(
            "Employment Status",
            ["employed", "self_employed", "retired", "unemployed"],
        )
        location = st.text_input("Location", value="")

        # Risk Tolerance
        st.subheader("Risk Tolerance")
        investment_experience = st.selectbox(
            "Investment Experience",
            ["beginner", "intermediate", "advanced"],
        )
        time_horizon = st.selectbox(
            "Investment Time Horizon",
            ["short", "medium", "long"],
        )
        loss_tolerance = st.selectbox(
            "Loss Tolerance",
            ["low", "medium", "high"],
        )

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            profile_data = {
                "demographics": {
                    "age": age,
                    "income": float(income),
                    "employment_status": employment_status,
                    "location": location,
                },
                "investment_experience": investment_experience,
                "risk_tolerance": {
                    "factors": {
                        "investment_experience": investment_experience,
                        "time_horizon": time_horizon,
                        "loss_tolerance": loss_tolerance,
                    },
                },
            }
            return profile_data

    return {}

