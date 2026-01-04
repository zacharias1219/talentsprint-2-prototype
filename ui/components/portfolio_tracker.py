"""
Portfolio Performance Tracking Component.

Tracks portfolio performance over time with snapshots, returns calculation,
and benchmark comparison (S&P 500).
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import json

# Directory for storing portfolio snapshots
PROJECT_ROOT = Path(__file__).parent.parent.parent
PORTFOLIO_DATA_DIR = PROJECT_ROOT / "data" / "portfolio_history"
PORTFOLIO_DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_portfolio_history(session_id: str) -> List[Dict]:
    """Load portfolio history for a user session."""
    file_path = PORTFOLIO_DATA_DIR / f"{session_id}_history.json"
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return []


def save_portfolio_snapshot(session_id: str, snapshot: Dict) -> None:
    """Save a portfolio snapshot."""
    history = load_portfolio_history(session_id)
    history.append(snapshot)
    
    file_path = PORTFOLIO_DATA_DIR / f"{session_id}_history.json"
    with open(file_path, 'w') as f:
        json.dump(history, f, indent=2)


def create_portfolio_snapshot(
    profile: Dict[str, Any],
    recommendation: Dict[str, Any],
    current_value: float
) -> Dict:
    """Create a portfolio snapshot with current data."""
    return {
        "timestamp": datetime.now().isoformat(),
        "total_value": current_value,
        "allocation": profile.get("current_portfolio", {}),
        "target_allocation": recommendation.get("target_allocation", {}),
        "risk_score": recommendation.get("risk_profile", {}).get("score", 50),
        "risk_label": recommendation.get("risk_profile", {}).get("label", "Moderate"),
    }


@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_calculated_historical_data(
    current_value: float,
    allocation: Dict[str, float],
    months: int = 12
) -> pd.DataFrame:
    """Generate calculated historical performance data based on actual portfolio allocation."""
    from components.portfolio_calculations import generate_portfolio_performance
    
    # Generate performance based on actual allocation
    df = generate_portfolio_performance(
        allocation=allocation,
        initial_value=current_value,
        months=months,
        include_benchmarks=True
    )
    
    # Return only portfolio and sp500 for compatibility
    return pd.DataFrame({
        'date': df['date'],
        'portfolio': df['portfolio'],
        'sp500': df['sp500']
    })


def calculate_performance_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Calculate portfolio performance metrics."""
    portfolio_return = (df['portfolio'].iloc[-1] / df['portfolio'].iloc[0] - 1) * 100
    sp500_return = (df['sp500'].iloc[-1] / df['sp500'].iloc[0] - 1) * 100
    
    # Daily returns for volatility
    portfolio_daily = df['portfolio'].pct_change().dropna()
    sp500_daily = df['sp500'].pct_change().dropna()
    
    portfolio_volatility = portfolio_daily.std() * np.sqrt(252) * 100
    sp500_volatility = sp500_daily.std() * np.sqrt(252) * 100
    
    # Sharpe ratio (assuming 4% risk-free rate)
    risk_free = 0.04
    portfolio_sharpe = (portfolio_return / 100 - risk_free) / (portfolio_volatility / 100) if portfolio_volatility > 0 else 0
    
    # Alpha (excess return vs benchmark)
    alpha = portfolio_return - sp500_return
    
    # Max drawdown
    portfolio_cummax = df['portfolio'].cummax()
    drawdown = (df['portfolio'] - portfolio_cummax) / portfolio_cummax
    max_drawdown = drawdown.min() * 100
    
    return {
        "portfolio_return": portfolio_return,
        "sp500_return": sp500_return,
        "alpha": alpha,
        "portfolio_volatility": portfolio_volatility,
        "sp500_volatility": sp500_volatility,
        "sharpe_ratio": portfolio_sharpe,
        "max_drawdown": max_drawdown,
    }


def render_performance_chart(df: pd.DataFrame, period_label: str) -> None:
    """Render portfolio vs benchmark performance chart."""
    fig = go.Figure()
    
    # Normalize to 100 for comparison
    portfolio_normalized = (df['portfolio'] / df['portfolio'].iloc[0]) * 100
    sp500_normalized = (df['sp500'] / df['sp500'].iloc[0]) * 100
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=portfolio_normalized,
        mode='lines',
        name='Your Portfolio',
        line=dict(color='#2E86AB', width=2.5)
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=sp500_normalized,
        mode='lines',
        name='S&P 500',
        line=dict(color='#A23B72', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"Portfolio Performance ({period_label})",
        xaxis_title="Date",
        yaxis_title="Value (Indexed to 100)",
        height=400,
        template="plotly_white",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )
    
    # Add shaded region between the two lines
    fig.add_trace(go.Scatter(
        x=pd.concat([df['date'], df['date'][::-1]]),
        y=pd.concat([portfolio_normalized, sp500_normalized[::-1]]),
        fill='toself',
        fillcolor='rgba(46, 134, 171, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    st.plotly_chart(fig, use_container_width=True)


def render_metrics_cards(metrics: Dict[str, float]) -> None:
    """Render performance metrics as cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Your Return",
            f"{metrics['portfolio_return']:.1f}%",
            delta=f"vs S&P: {metrics['alpha']:+.1f}%",
            delta_color="normal" if metrics['alpha'] >= 0 else "inverse"
        )
    
    with col2:
        st.metric(
            "S&P 500 Return",
            f"{metrics['sp500_return']:.1f}%"
        )
    
    with col3:
        st.metric(
            "Volatility",
            f"{metrics['portfolio_volatility']:.1f}%",
            delta=f"vs S&P: {metrics['portfolio_volatility'] - metrics['sp500_volatility']:+.1f}%",
            delta_color="inverse"  # Lower is better
        )
    
    with col4:
        st.metric(
            "Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.2f}",
            help="Risk-adjusted return. Higher is better. >1 is good, >2 is excellent."
        )
    
    # Second row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Alpha",
            f"{metrics['alpha']:+.1f}%",
            help="Excess return over benchmark"
        )
    
    with col2:
        st.metric(
            "Max Drawdown",
            f"{metrics['max_drawdown']:.1f}%",
            help="Largest peak-to-trough decline"
        )


def render_allocation_history_chart(history: List[Dict]) -> None:
    """Render allocation changes over time."""
    if not history or len(history) < 2:
        st.info("Need at least 2 snapshots to show allocation history.")
        return
    
    dates = [h['timestamp'][:10] for h in history]
    stocks = [h['allocation'].get('stocks', 50) for h in history]
    bonds = [h['allocation'].get('bonds', 30) for h in history]
    cash = [h['allocation'].get('cash', 20) for h in history]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates, y=stocks, mode='lines+markers', name='Stocks',
        line=dict(color='#2E86AB'), fill='tozeroy'
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=bonds, mode='lines+markers', name='Bonds',
        line=dict(color='#F18F01')
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=cash, mode='lines+markers', name='Cash',
        line=dict(color='#C73E1D')
    ))
    
    fig.update_layout(
        title="Allocation History",
        xaxis_title="Date",
        yaxis_title="Percentage (%)",
        height=300,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_portfolio_tracker(
    session_id: Optional[str],
    profile: Optional[Dict],
    recommendation: Optional[Dict]
) -> None:
    """Main portfolio tracker component."""
    st.header("📈 Portfolio Performance Tracker")
    
    if not profile or not recommendation:
        st.warning("Please create or select a session and generate recommendations first.")
        return
    
    # Portfolio value input
    st.subheader("💰 Your Portfolio")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        current_value = st.number_input(
            "Current Portfolio Value ($)",
            min_value=0.0,
            value=float(profile.get('savings', 10000)),
            step=1000.0,
            format="%.2f"
        )
    
    with col2:
        if st.button("📸 Save Snapshot", use_container_width=True):
            if session_id:
                snapshot = create_portfolio_snapshot(profile, recommendation, current_value)
                save_portfolio_snapshot(session_id, snapshot)
                st.success("✅ Portfolio snapshot saved!")
                st.rerun()
    
    st.divider()
    
    # Time period selector
    period = st.selectbox(
        "Performance Period",
        ["1 Month", "3 Months", "6 Months", "1 Year"],
        index=3
    )
    
    period_map = {"1 Month": 1, "3 Months": 3, "6 Months": 6, "1 Year": 12}
    months = period_map[period]
    
    # Use target allocation from recommendations (what user should aim for)
    # Fall back to current portfolio if target not available
    target_allocation = recommendation.get('target_allocation', {})
    if not target_allocation or sum(target_allocation.values()) == 0:
        # Fallback to current portfolio allocation
        allocation = profile.get('current_portfolio', {'stocks': 50, 'bonds': 30, 'cash': 20})
        allocation_label = "Current Portfolio"
    else:
        allocation = target_allocation
        allocation_label = "Recommended Portfolio"
    
    # Generate calculated data based on allocation
    df = generate_calculated_historical_data(current_value, allocation, months)
    metrics = calculate_performance_metrics(df)
    
    # Show which allocation is being used
    st.caption(f"📊 Performance based on: **{allocation_label}** ({allocation.get('stocks', 0)}% stocks, {allocation.get('bonds', 0)}% bonds, {allocation.get('cash', 0)}% cash)")
    
    # Performance Overview
    st.subheader("📊 Performance Overview")
    
    # Render metrics
    render_metrics_cards(metrics)
    
    st.divider()
    
    # Performance chart
    render_performance_chart(df, period)
    
    # Interpretation
    if metrics['alpha'] > 0:
        st.success(f"🎉 **Great job!** Your portfolio outperformed the S&P 500 by {metrics['alpha']:.1f}%")
    elif metrics['alpha'] < -5:
        st.warning(f"⚠️ Your portfolio underperformed the S&P 500 by {abs(metrics['alpha']):.1f}%. Consider reviewing your allocation.")
    else:
        st.info(f"📊 Your portfolio is performing in line with the market (within {abs(metrics['alpha']):.1f}%)")
    
    st.divider()
    
    # Historical snapshots
    st.subheader("📜 Portfolio History")
    
    if session_id:
        history = load_portfolio_history(session_id)
        
        if history:
            render_allocation_history_chart(history)
            
            with st.expander("View All Snapshots"):
                for i, snapshot in enumerate(reversed(history[-10:])):
                    st.write(f"**{snapshot['timestamp'][:19]}** - ${snapshot['total_value']:,.2f}")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f"Stocks: {snapshot['allocation'].get('stocks', 0)}%")
                    with col2:
                        st.caption(f"Bonds: {snapshot['allocation'].get('bonds', 0)}%")
                    with col3:
                        st.caption(f"Cash: {snapshot['allocation'].get('cash', 0)}%")
                    st.divider()
        else:
            st.info("No snapshots yet. Click 'Save Snapshot' to start tracking your portfolio.")
    else:
        st.info("Create a session to track portfolio history over time.")
    
    # Tips
    with st.expander("💡 Understanding Your Metrics"):
        st.markdown("""
        **Key Metrics Explained:**
        
        - **Return**: Total percentage gain/loss over the period
        - **Alpha**: Excess return compared to S&P 500 benchmark
        - **Volatility**: Standard deviation of returns (risk measure)
        - **Sharpe Ratio**: Risk-adjusted return (higher = better return for the risk taken)
        - **Max Drawdown**: Largest drop from peak to trough
        
        **What Good Looks Like:**
        - Positive alpha = beating the market
        - Sharpe > 1.0 = good risk-adjusted returns
        - Volatility lower than S&P = smoother ride
        """)

