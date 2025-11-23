"""
Visualization components for Streamlit UI.

Displays charts and graphs for recommendations and portfolio analysis.
"""

import streamlit as st
from typing import Any, Dict, List

from src.personalization.visualization_generator import VisualizationGenerator


def render_portfolio_allocation(recommendations: List[Dict[str, Any]]) -> None:
    """
    Render portfolio allocation chart.

    Args:
        recommendations: List of recommendations.
    """
    viz_gen = VisualizationGenerator()
    fig = viz_gen.generate_allocation_chart(recommendations)
    st.plotly_chart(fig, use_container_width=True)


def render_risk_return_chart(recommendations: List[Dict[str, Any]]) -> None:
    """
    Render risk-return scatter chart.

    Args:
        recommendations: List of recommendations.
    """
    viz_gen = VisualizationGenerator()
    fig = viz_gen.generate_risk_return_chart(recommendations)
    st.plotly_chart(fig, use_container_width=True)


def render_goal_progress(goal_data: Dict[str, Any]) -> None:
    """
    Render goal progress visualization.

    Args:
        goal_data: Goal data dictionary.
    """
    st.subheader(f"Goal: {goal_data.get('goal_type', 'Unknown')}")

    target = goal_data.get("target_amount", 0)
    current = goal_data.get("current_progress", 0)
    progress_pct = (current / target * 100) if target > 0 else 0

    st.progress(progress_pct / 100)
    st.write(f"Progress: ${current:,.2f} / ${target:,.2f} ({progress_pct:.1f}%)")

    if goal_data.get("required_monthly_contribution"):
        st.write(f"Required Monthly Contribution: ${goal_data['required_monthly_contribution']:,.2f}")

