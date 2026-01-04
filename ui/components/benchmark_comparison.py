"""
Benchmark Comparison Tool.

Compare portfolio performance to market benchmarks like S&P 500.
Shows side-by-side charts, Sharpe ratio, max drawdown, and other metrics.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_benchmark_data(
    stocks: float,
    bonds: float, 
    cash: float,
    initial_value: float = 10000,
    months: int = 12
) -> pd.DataFrame:
    """
    Generate calculated portfolio and benchmark performance data based on actual allocation.
    
    Uses historical asset class returns instead of random values.
    Note: Uses individual allocation values instead of dict for caching compatibility.
    """
    from components.portfolio_calculations import generate_portfolio_performance
    
    portfolio_allocation = {'stocks': stocks, 'bonds': bonds, 'cash': cash}
    
    # Generate performance based on actual allocation and historical averages
    df = generate_portfolio_performance(
        allocation=portfolio_allocation,
        initial_value=initial_value,
        months=months,
        include_benchmarks=True
    )
    
    return df


def calculate_metrics(returns: np.ndarray, name: str, annual_periods: int = 252) -> Dict[str, float]:
    """
    Calculate mathematically rigorous performance metrics for a return series.
    
    All calculations use standard financial mathematics:
    - Compound returns: exp(sum(log(1+r)))
    - Annualization: geometric mean
    - Volatility: standard deviation * sqrt(periods)
    - Sharpe: (return - risk_free) / volatility
    - Sortino: (return - risk_free) / downside_deviation
    - Drawdown: peak-to-trough decline
    """
    if len(returns) == 0:
        return {
            'name': name,
            'total_return': 0.0,
            'annualized_return': 0.0,
            'volatility': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'beta': 0.0,
            'correlation': 0.0,
        }
    
    # Total return: compound all returns mathematically
    # Using log returns: total = exp(sum(returns)) - 1
    total_return = (np.exp(np.sum(returns)) - 1) * 100
    
    # Annualized return: geometric mean
    # Formula: (1 + total_return)^(periods_per_year / periods) - 1
    days = len(returns)
    if days > 0:
        annualized_return = ((1 + total_return/100) ** (annual_periods / days) - 1) * 100
    else:
        annualized_return = 0.0
    
    # Volatility (annualized): standard deviation * sqrt(periods)
    # This is the mathematical definition of annualized volatility
    volatility = np.std(returns) * np.sqrt(annual_periods) * 100
    
    # Sharpe Ratio: (Return - Risk-Free) / Volatility
    # Standard formula for risk-adjusted return
    risk_free = 0.04  # 4% risk-free rate
    excess_return = annualized_return / 100 - risk_free
    sharpe = excess_return / (volatility / 100) if volatility > 0 else 0.0
    
    # Max Drawdown: largest peak-to-trough decline
    # Mathematical definition: max((peak - trough) / peak)
    cumulative = np.exp(np.cumsum(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = np.min(drawdown) * 100
    
    # Sortino Ratio: (Return - Risk-Free) / Downside Deviation
    # Only penalizes negative volatility (downside risk)
    downside_returns = returns[returns < 0]
    if len(downside_returns) > 0:
        downside_std = np.std(downside_returns) * np.sqrt(annual_periods)
        sortino = excess_return / downside_std if downside_std > 0 else 0.0
    else:
        sortino = np.inf if excess_return > 0 else 0.0  # No downside = perfect
    
    # Win rate: percentage of positive returns
    win_rate = (np.sum(returns > 0) / len(returns)) * 100 if len(returns) > 0 else 0.0
    
    # Beta and correlation (will be calculated in comparison context)
    # Placeholder values - will be calculated when comparing to benchmark
    beta = 1.0  # Default beta
    correlation = 0.0  # Will be calculated in comparison
    
    return {
        'name': name,
        'total_return': total_return,
        'annualized_return': annualized_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe,
        'sortino_ratio': sortino,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'beta': beta,
        'correlation': correlation,
    }


def render_comparison_chart(df: pd.DataFrame, benchmarks: List[str]) -> None:
    """Render side-by-side performance comparison chart."""
    
    fig = go.Figure()
    
    # Normalize all values to start at 100
    colors = {
        'portfolio': '#2E86AB',
        'sp500': '#A23B72',
        'nasdaq': '#F18F01',
        'balanced_60_40': '#C73E1D',
    }
    
    names = {
        'portfolio': 'Your Portfolio',
        'sp500': 'S&P 500',
        'nasdaq': 'NASDAQ',
        'balanced_60_40': '60/40 Balanced',
    }
    
    for col in ['portfolio'] + benchmarks:
        normalized = (df[col] / df[col].iloc[0]) * 100
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=normalized,
            mode='lines',
            name=names.get(col, col),
            line=dict(
                color=colors.get(col, '#888'),
                width=3 if col == 'portfolio' else 2,
            ),
        ))
    
    fig.update_layout(
        title="Portfolio vs Benchmarks (Indexed to 100)",
        xaxis_title="Date",
        yaxis_title="Value (Starting = 100)",
        height=450,
        template="plotly_white",
        hovermode='x unified',
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255,255,255,0.9)"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_metrics_comparison_table(metrics_list: List[Dict]) -> None:
    """Render a mathematically complete comparison table of performance metrics."""
    
    df = pd.DataFrame(metrics_list)
    df = df.set_index('name')
    
    # Format columns with all mathematical metrics
    styled_data = {
        'Total Return': [f"{v:+.1f}%" for v in df['total_return']],
        'Annual Return': [f"{v:+.1f}%" for v in df['annualized_return']],
        'Volatility': [f"{v:.1f}%" for v in df['volatility']],
        'Sharpe': [f"{v:.2f}" for v in df['sharpe_ratio']],
        'Sortino': [f"{v:.2f}" for v in df['sortino_ratio']],
        'Max Drawdown': [f"{v:.1f}%" for v in df['max_drawdown']],
        'Win Rate': [f"{v:.0f}%" for v in df['win_rate']],
    }
    
    # Add Beta and Correlation if available
    if 'beta' in df.columns and not df['beta'].isna().all():
        styled_data['Beta'] = [f"{v:.2f}" if not np.isnan(v) else "N/A" for v in df['beta']]
    if 'correlation' in df.columns and not df['correlation'].isna().all():
        styled_data['Correlation'] = [f"{v:.2f}" if not np.isnan(v) else "N/A" for v in df['correlation']]
    
    display_df = pd.DataFrame(styled_data, index=df.index)
    
    st.dataframe(display_df, use_container_width=True)


def render_metrics_cards(portfolio_metrics: Dict, benchmark_metrics: Dict) -> None:
    """Render comparison metric cards."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        diff = portfolio_metrics['total_return'] - benchmark_metrics['total_return']
        st.metric(
            "Your Return",
            f"{portfolio_metrics['total_return']:+.1f}%",
            delta=f"{diff:+.1f}% vs S&P",
            delta_color="normal" if diff >= 0 else "inverse"
        )
    
    with col2:
        vol_diff = portfolio_metrics['volatility'] - benchmark_metrics['volatility']
        st.metric(
            "Volatility",
            f"{portfolio_metrics['volatility']:.1f}%",
            delta=f"{vol_diff:+.1f}%",
            delta_color="inverse"  # Lower is better
        )
    
    with col3:
        sharpe_diff = portfolio_metrics['sharpe_ratio'] - benchmark_metrics['sharpe_ratio']
        st.metric(
            "Sharpe Ratio",
            f"{portfolio_metrics['sharpe_ratio']:.2f}",
            delta=f"{sharpe_diff:+.2f}",
            delta_color="normal"
        )
    
    with col4:
        dd_diff = portfolio_metrics['max_drawdown'] - benchmark_metrics['max_drawdown']
        st.metric(
            "Max Drawdown",
            f"{portfolio_metrics['max_drawdown']:.1f}%",
            delta=f"{dd_diff:+.1f}%",
            delta_color="inverse"  # Less negative is better
        )


def render_radar_chart(portfolio_metrics: Dict, benchmark_metrics: Dict) -> None:
    """
    Render radar chart with mathematically normalized scores.
    
    Uses min-max normalization to scale all metrics to 0-100 range:
    normalized = (value - min) / (max - min) * 100
    """
    
    categories = ['Return', 'Risk-Adj Return', 'Low Volatility', 'Max Drawdown', 'Consistency']
    
    # Collect all values for proper min-max normalization
    all_returns = [portfolio_metrics['annualized_return'], benchmark_metrics['annualized_return']]
    all_sharpes = [portfolio_metrics['sharpe_ratio'], benchmark_metrics['sharpe_ratio']]
    all_vols = [portfolio_metrics['volatility'], benchmark_metrics['volatility']]
    all_drawdowns = [portfolio_metrics['max_drawdown'], benchmark_metrics['max_drawdown']]
    all_win_rates = [portfolio_metrics['win_rate'], benchmark_metrics['win_rate']]
    
    # Min-max normalization function
    def normalize(value, min_val, max_val):
        if max_val == min_val:
            return 50.0  # Neutral if no range
        return ((value - min_val) / (max_val - min_val)) * 100
    
    # Normalize Return (higher is better)
    return_min, return_max = min(all_returns), max(all_returns)
    if return_max == return_min:
        return_max = return_min + 1  # Avoid division by zero
    portfolio_return_score = normalize(portfolio_metrics['annualized_return'], return_min, return_max)
    benchmark_return_score = normalize(benchmark_metrics['annualized_return'], return_min, return_max)
    
    # Normalize Sharpe Ratio (higher is better)
    sharpe_min, sharpe_max = min(all_sharpes), max(all_sharpes)
    if sharpe_max == sharpe_min:
        sharpe_max = sharpe_min + 1
    portfolio_sharpe_score = normalize(portfolio_metrics['sharpe_ratio'], sharpe_min, sharpe_max)
    benchmark_sharpe_score = normalize(benchmark_metrics['sharpe_ratio'], sharpe_min, sharpe_max)
    
    # Normalize Volatility (lower is better, so invert)
    vol_min, vol_max = min(all_vols), max(all_vols)
    if vol_max == vol_min:
        vol_max = vol_min + 1
    portfolio_vol_score = 100 - normalize(portfolio_metrics['volatility'], vol_min, vol_max)
    benchmark_vol_score = 100 - normalize(benchmark_metrics['volatility'], vol_min, vol_max)
    
    # Normalize Drawdown (less negative is better, so invert)
    dd_min, dd_max = min(all_drawdowns), max(all_drawdowns)
    if dd_max == dd_min:
        dd_max = dd_min + 1
    portfolio_dd_score = 100 - normalize(portfolio_metrics['max_drawdown'], dd_min, dd_max)
    benchmark_dd_score = 100 - normalize(benchmark_metrics['max_drawdown'], dd_min, dd_max)
    
    # Win Rate (already 0-100, but normalize for consistency)
    wr_min, wr_max = min(all_win_rates), max(all_win_rates)
    if wr_max == wr_min:
        wr_max = wr_min + 1
    portfolio_wr_score = normalize(portfolio_metrics['win_rate'], wr_min, wr_max)
    benchmark_wr_score = normalize(benchmark_metrics['win_rate'], wr_min, wr_max)
    
    portfolio_scores = [
        max(0, min(100, portfolio_return_score)),
        max(0, min(100, portfolio_sharpe_score)),
        max(0, min(100, portfolio_vol_score)),
        max(0, min(100, portfolio_dd_score)),
        max(0, min(100, portfolio_wr_score)),
    ]
    
    benchmark_scores = [
        max(0, min(100, benchmark_return_score)),
        max(0, min(100, benchmark_sharpe_score)),
        max(0, min(100, benchmark_vol_score)),
        max(0, min(100, benchmark_dd_score)),
        max(0, min(100, benchmark_wr_score)),
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=portfolio_scores + [portfolio_scores[0]],  # Close the shape
        theta=categories + [categories[0]],
        fill='toself',
        name='Your Portfolio',
        line_color='#2E86AB',
        fillcolor='rgba(46, 134, 171, 0.3)'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=benchmark_scores + [benchmark_scores[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='S&P 500',
        line_color='#A23B72',
        fillcolor='rgba(162, 59, 114, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title="Portfolio Characteristics Comparison",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_benchmark_comparison(
    profile: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]]
) -> None:
    """Main benchmark comparison component - completely mathematical."""
    
    st.header("📊 Benchmark Comparison Tool")
    
    if not profile:
        st.warning("Please create or select a session first to see portfolio comparison.")
        return
    
    # Use target allocation from recommendations (mathematically optimal)
    # Fall back to current portfolio if target not available
    if recommendation and recommendation.get('target_allocation'):
        portfolio_allocation = recommendation.get('target_allocation', {})
        allocation_label = "Recommended Portfolio"
    else:
        portfolio_allocation = profile.get('current_portfolio', {
            'stocks': 50, 'bonds': 30, 'cash': 20
        })
        allocation_label = "Current Portfolio"
    
    # Ensure allocation sums to 100% (mathematical requirement)
    total = sum(portfolio_allocation.values())
    if total != 100 and total > 0:
        scale = 100 / total
        portfolio_allocation = {
            k: v * scale for k, v in portfolio_allocation.items()
        }
    
    st.caption(f"📊 Comparing: **{allocation_label}** ({portfolio_allocation.get('stocks', 0):.1f}% stocks, {portfolio_allocation.get('bonds', 0):.1f}% bonds, {portfolio_allocation.get('cash', 0):.1f}% cash)")
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        time_period = st.selectbox(
            "Time Period",
            ["3 Months", "6 Months", "1 Year", "3 Years"],
            index=2
        )
    
    with col2:
        benchmarks = st.multiselect(
            "Compare Against",
            ["sp500", "nasdaq", "balanced_60_40"],
            default=["sp500"],
            format_func=lambda x: {
                "sp500": "S&P 500",
                "nasdaq": "NASDAQ",
                "balanced_60_40": "60/40 Balanced"
            }.get(x, x)
        )
    
    period_map = {"3 Months": 3, "6 Months": 6, "1 Year": 12, "3 Years": 36}
    months = period_map[time_period]
    
    # Generate data
    initial_value = float(profile.get('savings', 10000))
    df = generate_benchmark_data(
        stocks=portfolio_allocation.get('stocks', 50),
        bonds=portfolio_allocation.get('bonds', 30),
        cash=portfolio_allocation.get('cash', 20),
        initial_value=initial_value,
        months=months
    )
    
    # Calculate metrics mathematically
    portfolio_returns = df['portfolio_returns'].values
    portfolio_metrics = calculate_metrics(portfolio_returns, "Your Portfolio")
    
    metrics_list = [portfolio_metrics]
    benchmark_metrics = None
    
    # Calculate metrics for each benchmark
    for bench in benchmarks:
        bench_returns = df[f'{bench}_returns'].values
        bench_metrics = calculate_metrics(
            bench_returns,
            {"sp500": "S&P 500", "nasdaq": "NASDAQ", "balanced_60_40": "60/40 Balanced"}[bench]
        )
        
        # Calculate Beta and Correlation mathematically
        # Beta = Covariance(portfolio, benchmark) / Variance(benchmark)
        # Correlation = Covariance(portfolio, benchmark) / (std(portfolio) * std(benchmark))
        if len(portfolio_returns) == len(bench_returns) and len(portfolio_returns) > 1:
            covariance = np.cov(portfolio_returns, bench_returns)[0, 1]
            bench_variance = np.var(bench_returns)
            portfolio_std = np.std(portfolio_returns)
            bench_std = np.std(bench_returns)
            
            if bench_variance > 0:
                beta = covariance / bench_variance
            else:
                beta = 1.0
            
            if portfolio_std > 0 and bench_std > 0:
                correlation = covariance / (portfolio_std * bench_std)
            else:
                correlation = 0.0
            
            bench_metrics['beta'] = beta
            bench_metrics['correlation'] = correlation
            
            # Also update portfolio metrics with beta/correlation for primary benchmark
            if bench == 'sp500' or benchmark_metrics is None:
                portfolio_metrics['beta'] = beta
                portfolio_metrics['correlation'] = correlation
        
        metrics_list.append(bench_metrics)
        if bench == 'sp500':
            benchmark_metrics = bench_metrics
    
    if benchmark_metrics is None and len(metrics_list) > 1:
        benchmark_metrics = metrics_list[1]
    elif benchmark_metrics is None:
        # Calculate S&P 500 metrics as default benchmark
        sp500_returns = df['sp500_returns'].values
        benchmark_metrics = calculate_metrics(sp500_returns, "S&P 500")
        
        # Calculate beta and correlation
        if len(portfolio_returns) == len(sp500_returns) and len(portfolio_returns) > 1:
            covariance = np.cov(portfolio_returns, sp500_returns)[0, 1]
            sp500_variance = np.var(sp500_returns)
            portfolio_std = np.std(portfolio_returns)
            sp500_std = np.std(sp500_returns)
            
            if sp500_variance > 0:
                beta = covariance / sp500_variance
            else:
                beta = 1.0
            
            if portfolio_std > 0 and sp500_std > 0:
                correlation = covariance / (portfolio_std * sp500_std)
            else:
                correlation = 0.0
            
            portfolio_metrics['beta'] = beta
            portfolio_metrics['correlation'] = correlation
            benchmark_metrics['beta'] = 1.0  # S&P 500 has beta of 1.0 by definition
            benchmark_metrics['correlation'] = correlation
    
    st.divider()
    
    # Key Metrics Cards
    st.subheader("📈 Performance Summary")
    render_metrics_cards(portfolio_metrics, benchmark_metrics)
    
    st.divider()
    
    # Performance Chart
    st.subheader("📉 Performance Over Time")
    render_comparison_chart(df, benchmarks)
    
    st.divider()
    
    # Metrics Table
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("📋 Detailed Metrics")
        render_metrics_comparison_table(metrics_list)
    
    with col2:
        st.subheader("🎯 Risk Profile")
        render_radar_chart(portfolio_metrics, benchmark_metrics)
    
    # Analysis
    st.divider()
    st.subheader("📝 Analysis")
    
    alpha = portfolio_metrics['total_return'] - benchmark_metrics['total_return']
    sharpe_diff = portfolio_metrics['sharpe_ratio'] - benchmark_metrics['sharpe_ratio']
    
    if alpha > 0 and sharpe_diff > 0:
        st.success(f"""
        **Excellent!** Your portfolio outperformed the benchmark by **{alpha:+.1f}%** 
        with a better risk-adjusted return (Sharpe: {portfolio_metrics['sharpe_ratio']:.2f} vs {benchmark_metrics['sharpe_ratio']:.2f}).
        
        This suggests your allocation is well-suited to your risk profile.
        """)
    elif alpha > 0:
        st.info(f"""
        **Good returns!** Your portfolio beat the benchmark by **{alpha:+.1f}%**, 
        but with slightly higher risk-adjusted metrics to watch.
        
        Consider if the extra volatility aligns with your goals.
        """)
    elif sharpe_diff > 0:
        st.info(f"""
        **Solid risk management!** While your total return was {abs(alpha):.1f}% below the benchmark, 
        your risk-adjusted return (Sharpe) is actually better.
        
        You're getting better returns per unit of risk taken.
        """)
    else:
        st.warning(f"""
        **Room for improvement.** Your portfolio underperformed by **{alpha:.1f}%** 
        with lower risk-adjusted returns.
        
        Consider reviewing your allocation or consulting your action plan.
        """)
    
    # Mathematical formulas and explanations
    with st.expander("📚 Mathematical Formulas & Metrics"):
        st.markdown("""
        ### **Mathematical Definitions:**
        
        | Metric | Formula | Description |
        |--------|---------|-------------|
        | **Total Return** | `R_total = (exp(Σr_i) - 1) × 100%` | Compound return over period |
        | **Annualized Return** | `R_annual = (1 + R_total)^(252/days) - 1` | Geometric mean return |
        | **Volatility** | `σ = std(r) × √252 × 100%` | Annualized standard deviation |
        | **Sharpe Ratio** | `S = (R_annual - R_f) / σ` | Risk-adjusted return (R_f = 4%) |
        | **Sortino Ratio** | `S_d = (R_annual - R_f) / σ_downside` | Downside risk-adjusted return |
        | **Max Drawdown** | `DD = min((peak - value) / peak)` | Largest peak-to-trough decline |
        | **Beta** | `β = Cov(r_p, r_b) / Var(r_b)` | Sensitivity to market movements |
        | **Correlation** | `ρ = Cov(r_p, r_b) / (σ_p × σ_b)` | Linear relationship strength |
        | **Win Rate** | `WR = (positive_days / total_days) × 100%` | Percentage of positive returns |
        
        Where:
        - `r_i` = daily log returns
        - `r_p` = portfolio returns
        - `r_b` = benchmark returns
        - `R_f` = risk-free rate (4%)
        - `σ_downside` = standard deviation of negative returns only
        
        ### **Interpretation:**
        - **Total Return**: Overall gain/loss for the period
        - **Annualized Return**: Return adjusted to yearly rate (7-10% typical for stocks)
        - **Volatility**: Standard deviation of returns (lower = smoother ride)
        - **Sharpe Ratio**: Return per unit of risk (> 1.0 is good, > 2.0 is excellent)
        - **Sortino Ratio**: Return per unit of downside risk (higher than Sharpe is ideal)
        - **Max Drawdown**: Largest peak-to-trough decline (less negative is better)
        - **Beta**: Portfolio sensitivity (β = 1.0 = moves with market, β < 1.0 = less volatile)
        - **Correlation**: How closely portfolio tracks benchmark (1.0 = perfect correlation)
        - **Win Rate**: % of positive days (> 50% is typical)
        """)

