"""
User profile form component for Streamlit.
"""

import streamlit as st
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List


def load_user_recommendations(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Load user recommendations from JSON file.
    
    Args:
        user_id: User identifier
        
    Returns:
        User recommendation dictionary or None if not found
    """
    recs_path = Path(__file__).parent.parent.parent / "data" / "processed" / "user_recommendations.json"
    
    if not recs_path.exists():
        return None
    
    try:
        with open(recs_path, 'r') as f:
            all_recs = json.load(f)
        
        # Find user recommendation
        user_rec = next((r for r in all_recs if r.get("user_id") == user_id), None)
        return user_rec
    except Exception as e:
        st.error(f"Error loading recommendations: {e}")
        return None


def display_user_recommendations(user_id: str) -> None:
    """
    Display user recommendations including risk profile, allocation, and action plan.
    
    Args:
        user_id: User identifier
    """
    user_rec = load_user_recommendations(user_id)
    
    if not user_rec:
        st.info("No recommendations found for this user. Please generate recommendations first.")
        return
    
    st.header("📊 Your Financial Recommendations")
    
    # Risk Profile Section
    if "risk_profile" in user_rec:
        risk_profile = user_rec["risk_profile"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Risk Score", f"{risk_profile.get('score', 'N/A')}/100")
        with col2:
            st.metric("Risk Profile", risk_profile.get("label", "Unknown"))
    
    # Target Allocation Section
    if "target_allocation" in user_rec:
        st.subheader("🎯 Target Portfolio Allocation")
        allocation = user_rec["target_allocation"]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stocks", f"{allocation.get('stocks', 0)}%")
        with col2:
            st.metric("Bonds", f"{allocation.get('bonds', 0)}%")
        with col3:
            st.metric("Cash", f"{allocation.get('cash', 0)}%")
    
    # Allocation Gaps
    if "allocation_gaps" in user_rec:
        st.subheader("📈 Portfolio Adjustments Needed")
        gaps = user_rec["allocation_gaps"]
        for asset, gap in gaps.items():
            if abs(gap) > 1:  # Only show significant gaps
                st.write(f"**{asset.capitalize()}**: {'+' if gap > 0 else ''}{gap:.1f}%")
    
    # Suggested Sectors
    if "suggested_sectors" in user_rec and user_rec["suggested_sectors"]:
        st.subheader("🏢 Recommended Sectors")
        sectors = user_rec["suggested_sectors"]
        st.write(", ".join(sectors))
    
    # Action Plan
    if "action_plan" in user_rec and user_rec["action_plan"]:
        st.subheader("✅ Action Plan")
        for i, action in enumerate(user_rec["action_plan"], 1):
            st.write(f"{i}. {action}")


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
        savings = st.number_input("Current Savings ($)", min_value=0, value=10000)
        employment_status = st.selectbox(
            "Employment Status",
            ["employed", "self_employed", "retired", "unemployed"],
        )

        # Risk Tolerance
        st.subheader("Risk Tolerance")
        risk_tolerance = st.selectbox(
            "Risk Tolerance",
            ["Low", "Moderate", "High", "Very High"],
        )
        investment_horizon = st.number_input(
            "Investment Horizon (years)",
            min_value=1,
            max_value=50,
            value=10
        )
        
        # Financial Goals
        st.subheader("Financial Goals")
        goals = st.multiselect(
            "Select your financial goals",
            ["Retirement", "Home Purchase", "Wealth Generation", "Education", "Emergency Fund"],
            default=["Retirement"]
        )
        
        # Current Portfolio
        st.subheader("Current Portfolio Allocation")
        col1, col2, col3 = st.columns(3)
        with col1:
            stocks_pct = st.slider("Stocks (%)", 0, 100, 50)
        with col2:
            bonds_pct = st.slider("Bonds (%)", 0, 100, 30)
        with col3:
            cash_pct = st.slider("Cash (%)", 0, 100, 20)

        submitted = st.form_submit_button("Save Profile")

        if submitted:
            profile_data = {
                "age": age,
                "income": float(income),
                "savings": float(savings),
                "risk_tolerance": risk_tolerance,
                "investment_horizon_years": investment_horizon,
                "financial_goals": goals,
                "current_portfolio": {
                    "stocks": stocks_pct,
                    "bonds": bonds_pct,
                    "cash": cash_pct
                }
            }
            return profile_data

    return {}

