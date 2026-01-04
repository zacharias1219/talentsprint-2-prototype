"""
Visualization components for Streamlit UI.

Displays charts and graphs for recommendations and portfolio analysis.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Any, Dict, List, Optional
import pandas as pd


def render_portfolio_allocation(user_rec: Dict[str, Any]) -> None:
    """
    Render portfolio allocation pie chart (target allocation).

    Args:
        user_rec: User recommendation dictionary with target_allocation.
    """
    if "target_allocation" not in user_rec:
        st.warning("No allocation data available.")
        return
    
    allocation = user_rec["target_allocation"]
    labels = list(allocation.keys())
    values = list(allocation.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=[l.capitalize() for l in labels],
        values=values,
        hole=0.3,
        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c']
    )])
    
    fig.update_layout(
        title="Target Portfolio Allocation",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_allocation_comparison(user_rec: Dict[str, Any], profile: Optional[Dict[str, Any]] = None) -> None:
    """
    Render comparison chart showing current vs target allocation.

    Args:
        user_rec: User recommendation dictionary with allocation_gaps.
        profile: Optional user profile dictionary with current_portfolio.
    """
    if "allocation_gaps" not in user_rec:
        st.warning("No allocation comparison data available.")
        return
    
    # Get current allocation from profile if provided, otherwise from session state
    if profile and "current_portfolio" in profile:
        current_allocation = profile["current_portfolio"]
    else:
        # Try to get from session state (st is already imported at module level)
        if hasattr(st, 'session_state') and st.session_state.get('user_profile'):
            current_allocation = st.session_state.user_profile.get("current_portfolio", {})
        else:
            st.warning("Current portfolio allocation not available.")
            return
    
    target_allocation = user_rec.get("target_allocation", {})
    
    if not current_allocation or not target_allocation:
        st.warning("Incomplete allocation data.")
        return
    
    # Create comparison dataframe
    assets = list(target_allocation.keys())
    current_values = [current_allocation.get(a, 0) for a in assets]
    target_values = [target_allocation.get(a, 0) for a in assets]
    
    df = pd.DataFrame({
        'Asset': [a.capitalize() for a in assets],
        'Current': current_values,
        'Target': target_values
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Current',
        x=df['Asset'],
        y=df['Current'],
        marker_color='lightblue'
    ))
    
    fig.add_trace(go.Bar(
        name='Target',
        x=df['Asset'],
        y=df['Target'],
        marker_color='darkblue'
    ))
    
    fig.update_layout(
        title="Current vs Target Allocation",
        xaxis_title="Asset Class",
        yaxis_title="Percentage (%)",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_sector_recommendations(user_rec: Dict[str, Any]) -> None:
    """
    Display sector recommendations as bar chart.

    Args:
        user_rec: User recommendation dictionary with suggested_sectors.
    """
    if "suggested_sectors" not in user_rec or not user_rec["suggested_sectors"]:
        st.info("No sector recommendations available.")
        return
    
    sectors = user_rec["suggested_sectors"]
    # Create simple bar chart with equal weights (could be enhanced with actual weights)
    sector_counts = {sector: 1 for sector in sectors}
    
    df = pd.DataFrame({
        'Sector': list(sector_counts.keys()),
        'Recommendation Score': list(sector_counts.values())
    })
    
    fig = px.bar(
        df,
        x='Sector',
        y='Recommendation Score',
        title="Recommended Sectors",
        color='Recommendation Score',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


def render_risk_return_chart(user_rec: Dict[str, Any]) -> None:
    """
    Render risk-return visualization based on risk profile.

    Args:
        user_rec: User recommendation dictionary with risk_profile.
    """
    if "risk_profile" not in user_rec:
        st.warning("No risk profile data available.")
        return
    
    risk_score = user_rec["risk_profile"].get("score", 50)
    risk_label = user_rec["risk_profile"].get("label", "Unknown")
    
    # Create a simple risk-return scatter
    # In a real system, this would show actual portfolio options
    fig = go.Figure()
    
    # Add user's position
    fig.add_trace(go.Scatter(
        x=[risk_score],
        y=[risk_score * 0.8],  # Simplified return estimate
        mode='markers',
        marker=dict(size=20, color='red', symbol='star'),
        name='Your Profile',
        text=[risk_label],
        textposition="top center"
    ))
    
    # Add reference points
    reference_points = [
        {"risk": 20, "return": 15, "label": "Conservative"},
        {"risk": 50, "return": 40, "label": "Moderate"},
        {"risk": 80, "return": 65, "label": "Aggressive"}
    ]
    
    for point in reference_points:
        fig.add_trace(go.Scatter(
            x=[point["risk"]],
            y=[point["return"]],
            mode='markers',
            marker=dict(size=10, color='lightblue'),
            name=point["label"],
            showlegend=False
        ))
    
    fig.update_layout(
        title="Risk-Return Profile",
        xaxis_title="Risk Score",
        yaxis_title="Expected Return (%)",
        height=400
    )
    
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

