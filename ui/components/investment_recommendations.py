"""
Personalized Investment Recommendations Component.

Suggests specific ETFs and stocks based on user profile, risk tolerance,
and financial goals. Uses Alpha Vantage for real market data with rate limiting.
"""

import streamlit as st
import requests
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Add src to path for rate limiter
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

# Import rate limiter
try:
    from utils.rate_limiter import get_alpha_vantage_limiter, format_rate_limit_status
    RATE_LIMITER = get_alpha_vantage_limiter()
except ImportError:
    RATE_LIMITER = None


# ============================================================================
# ETF DATABASE - Curated recommendations by category
# ============================================================================

ETF_DATABASE = {
    # Total Market / Core Holdings
    "total_market": [
        {
            "symbol": "VTI",
            "name": "Vanguard Total Stock Market ETF",
            "category": "Total US Market",
            "expense_ratio": 0.03,
            "risk_level": "moderate",
            "description": "Covers entire US stock market",
            "suitable_for": ["growth", "long_term", "diversification"],
        },
        {
            "symbol": "VOO",
            "name": "Vanguard S&P 500 ETF",
            "category": "Large Cap Blend",
            "expense_ratio": 0.03,
            "risk_level": "moderate",
            "description": "Tracks S&P 500 index",
            "suitable_for": ["growth", "long_term", "core"],
        },
        {
            "symbol": "SPY",
            "name": "SPDR S&P 500 ETF Trust",
            "category": "Large Cap Blend",
            "expense_ratio": 0.09,
            "risk_level": "moderate",
            "description": "Most liquid S&P 500 ETF",
            "suitable_for": ["growth", "trading", "core"],
        },
    ],
    
    # Growth ETFs
    "growth": [
        {
            "symbol": "QQQ",
            "name": "Invesco QQQ Trust",
            "category": "Large Cap Growth",
            "expense_ratio": 0.20,
            "risk_level": "high",
            "description": "Tracks Nasdaq-100, tech-heavy",
            "suitable_for": ["aggressive_growth", "tech"],
        },
        {
            "symbol": "VUG",
            "name": "Vanguard Growth ETF",
            "category": "Large Cap Growth",
            "expense_ratio": 0.04,
            "risk_level": "moderate_high",
            "description": "US large-cap growth stocks",
            "suitable_for": ["growth", "long_term"],
        },
        {
            "symbol": "ARKK",
            "name": "ARK Innovation ETF",
            "category": "Disruptive Innovation",
            "expense_ratio": 0.75,
            "risk_level": "very_high",
            "description": "Disruptive technology companies",
            "suitable_for": ["speculative", "innovation"],
        },
    ],
    
    # Value ETFs
    "value": [
        {
            "symbol": "VTV",
            "name": "Vanguard Value ETF",
            "category": "Large Cap Value",
            "expense_ratio": 0.04,
            "risk_level": "moderate",
            "description": "US large-cap value stocks",
            "suitable_for": ["value", "income", "stability"],
        },
        {
            "symbol": "SCHD",
            "name": "Schwab US Dividend Equity ETF",
            "category": "Dividend",
            "expense_ratio": 0.06,
            "risk_level": "moderate_low",
            "description": "High dividend yield stocks",
            "suitable_for": ["income", "dividends", "stability"],
        },
    ],
    
    # Dividend ETFs
    "dividend": [
        {
            "symbol": "VYM",
            "name": "Vanguard High Dividend Yield ETF",
            "category": "High Dividend",
            "expense_ratio": 0.06,
            "risk_level": "moderate_low",
            "description": "High dividend US stocks",
            "suitable_for": ["income", "retirement", "dividends"],
        },
        {
            "symbol": "DVY",
            "name": "iShares Select Dividend ETF",
            "category": "Dividend Select",
            "expense_ratio": 0.38,
            "risk_level": "moderate_low",
            "description": "Dividend aristocrats focus",
            "suitable_for": ["income", "dividends", "stability"],
        },
    ],
    
    # Bond ETFs
    "bonds": [
        {
            "symbol": "BND",
            "name": "Vanguard Total Bond Market ETF",
            "category": "Total Bond Market",
            "expense_ratio": 0.03,
            "risk_level": "low",
            "description": "Diversified US bonds",
            "suitable_for": ["income", "stability", "conservative"],
        },
        {
            "symbol": "AGG",
            "name": "iShares Core US Aggregate Bond ETF",
            "category": "Total Bond Market",
            "expense_ratio": 0.03,
            "risk_level": "low",
            "description": "US investment-grade bonds",
            "suitable_for": ["income", "stability", "conservative"],
        },
        {
            "symbol": "TLT",
            "name": "iShares 20+ Year Treasury Bond ETF",
            "category": "Long-Term Treasury",
            "expense_ratio": 0.15,
            "risk_level": "moderate",
            "description": "Long-term US Treasuries",
            "suitable_for": ["safety", "interest_rate_bet"],
        },
    ],
    
    # International ETFs
    "international": [
        {
            "symbol": "VXUS",
            "name": "Vanguard Total International Stock ETF",
            "category": "International Equity",
            "expense_ratio": 0.07,
            "risk_level": "moderate_high",
            "description": "Non-US developed & emerging markets",
            "suitable_for": ["diversification", "international"],
        },
        {
            "symbol": "VEA",
            "name": "Vanguard FTSE Developed Markets ETF",
            "category": "Developed International",
            "expense_ratio": 0.05,
            "risk_level": "moderate",
            "description": "Developed markets ex-US",
            "suitable_for": ["diversification", "developed_markets"],
        },
        {
            "symbol": "VWO",
            "name": "Vanguard FTSE Emerging Markets ETF",
            "category": "Emerging Markets",
            "expense_ratio": 0.08,
            "risk_level": "high",
            "description": "Emerging market stocks",
            "suitable_for": ["growth", "emerging_markets", "aggressive"],
        },
    ],
    
    # Sector ETFs
    "technology": [
        {
            "symbol": "VGT",
            "name": "Vanguard Information Technology ETF",
            "category": "Technology",
            "expense_ratio": 0.10,
            "risk_level": "high",
            "description": "US tech sector",
            "suitable_for": ["growth", "tech", "sector_bet"],
        },
    ],
    "healthcare": [
        {
            "symbol": "VHT",
            "name": "Vanguard Health Care ETF",
            "category": "Healthcare",
            "expense_ratio": 0.10,
            "risk_level": "moderate_high",
            "description": "US healthcare sector",
            "suitable_for": ["growth", "healthcare", "defensive"],
        },
    ],
    "real_estate": [
        {
            "symbol": "VNQ",
            "name": "Vanguard Real Estate ETF",
            "category": "Real Estate",
            "expense_ratio": 0.12,
            "risk_level": "moderate_high",
            "description": "US REITs",
            "suitable_for": ["income", "real_estate", "inflation_hedge"],
        },
    ],
}


# ============================================================================
# PROFILE TO RECOMMENDATION MAPPING
# ============================================================================

def map_profile_to_etf_categories(profile: Dict[str, Any], recommendation: Dict[str, Any]) -> List[str]:
    """Map user profile to relevant ETF categories."""
    categories = []
    
    risk_tolerance = profile.get('risk_tolerance', 'Moderate')
    age = profile.get('age', 35)
    horizon = profile.get('investment_horizon_years', 10)
    goals = profile.get('financial_goals', [])
    target_allocation = recommendation.get('target_allocation', {})
    
    # Age-based adjustments
    if age < 35:
        categories.append('growth')
        if risk_tolerance in ['High', 'Very High']:
            categories.append('technology')
    elif age > 55:
        categories.append('dividend')
        categories.append('bonds')
    
    # Risk-based adjustments
    if risk_tolerance == 'Low':
        categories.extend(['bonds', 'dividend', 'value'])
    elif risk_tolerance == 'Moderate':
        categories.extend(['total_market', 'value', 'international'])
    elif risk_tolerance == 'High':
        categories.extend(['growth', 'international', 'technology'])
    elif risk_tolerance == 'Very High':
        categories.extend(['growth', 'technology'])
    
    # Goal-based adjustments
    if 'Retirement' in goals:
        categories.append('total_market')
        if age > 50:
            categories.append('dividend')
    if 'Wealth Generation' in goals:
        categories.append('growth')
    if 'Home Purchase' in goals and horizon < 5:
        categories.append('bonds')
    
    # Allocation-based adjustments
    if target_allocation.get('stocks', 0) > 70:
        categories.append('total_market')
    if target_allocation.get('bonds', 0) > 30:
        categories.append('bonds')
    
    # Always include diversification
    categories.append('international')
    
    return list(set(categories))


def build_recommended_portfolio(
    profile: Dict[str, Any],
    recommendation: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Build a personalized ETF portfolio recommendation that sums to 100%."""
    
    categories = map_profile_to_etf_categories(profile, recommendation)
    target_allocation = recommendation.get('target_allocation', {'stocks': 60, 'bonds': 30, 'cash': 10})
    
    portfolio = []
    stock_budget = target_allocation.get('stocks', 60)
    bond_budget = target_allocation.get('bonds', 30)
    cash_budget = target_allocation.get('cash', 10)
    
    # Ensure allocations sum to 100%
    total_budget = stock_budget + bond_budget + cash_budget
    if total_budget != 100:
        # Normalize to 100%
        scale = 100 / total_budget if total_budget > 0 else 1
        stock_budget = int(stock_budget * scale)
        bond_budget = int(bond_budget * scale)
        cash_budget = 100 - stock_budget - bond_budget  # Ensure exact 100%
    
    remaining_stock = stock_budget
    
    # Core holding (40-50% of stock allocation)
    core_pct = max(30, int(stock_budget * 0.45))
    core_pct = min(core_pct, remaining_stock)
    if core_pct > 0:
        portfolio.append({
            **ETF_DATABASE['total_market'][0],  # VTI
            'allocation': core_pct,
            'rationale': 'Core holding for broad US market exposure'
        })
        remaining_stock -= core_pct
    
    # Growth or Value based on profile
    if 'growth' in categories and remaining_stock > 5:
        growth_pct = min(25, int(remaining_stock * 0.4))
        if growth_pct > 0:
            portfolio.append({
                **ETF_DATABASE['growth'][0],  # QQQ
                'allocation': growth_pct,
                'rationale': 'Growth exposure for wealth accumulation'
            })
            remaining_stock -= growth_pct
    
    # Technology if high risk and in categories
    if 'technology' in categories and remaining_stock > 5:
        tech_pct = min(15, remaining_stock)
        if tech_pct > 0:
            portfolio.append({
                **ETF_DATABASE['technology'][0],  # QQQ (or could use tech-specific)
                'allocation': tech_pct,
                'rationale': 'Technology sector for aggressive growth'
            })
            remaining_stock -= tech_pct
    
    # Dividend/Value for income and stability
    if 'dividend' in categories and remaining_stock > 5:
        div_pct = min(20, remaining_stock)
        if div_pct > 0:
            portfolio.append({
                **ETF_DATABASE['dividend'][0],  # VYM
                'allocation': div_pct,
                'rationale': 'Dividend income for stability and passive income'
            })
            remaining_stock -= div_pct
    
    # Value stocks for lower risk growth
    if 'value' in categories and remaining_stock > 5:
        value_pct = min(20, remaining_stock)
        if value_pct > 0:
            portfolio.append({
                **ETF_DATABASE['value'][0],  # VTV
                'allocation': value_pct,
                'rationale': 'Value stocks for lower-risk growth potential'
            })
            remaining_stock -= value_pct
    
    # International diversification (always include some if stock budget allows)
    if remaining_stock > 5:
        intl_pct = min(20, remaining_stock)
        if intl_pct > 0:
            portfolio.append({
                **ETF_DATABASE['international'][0],  # VXUS
                'allocation': intl_pct,
                'rationale': 'International diversification to reduce US-only risk'
            })
            remaining_stock -= intl_pct
    
    # Add any remaining stock allocation to core holding
    if remaining_stock > 0:
        # Find core holding and add remaining
        for etf in portfolio:
            if etf['symbol'] == 'VTI':
                etf['allocation'] += remaining_stock
                remaining_stock = 0
                break
        # If no core holding found, add it
        if remaining_stock > 0:
            portfolio.insert(0, {
                **ETF_DATABASE['total_market'][0],
                'allocation': remaining_stock,
                'rationale': 'Additional core market exposure'
            })
    
    # Bond allocation
    if bond_budget > 0:
        portfolio.append({
            **ETF_DATABASE['bonds'][0],  # BND
            'allocation': bond_budget,
            'rationale': 'Fixed income for stability and income'
        })
    
    # Cash allocation (show as recommendation, not an ETF)
    if cash_budget > 0:
        portfolio.append({
            'symbol': 'CASH',
            'name': 'Cash / Money Market',
            'category': 'Cash Equivalent',
            'expense_ratio': 0.0,
            'risk_level': 'very_low',
            'description': 'High-yield savings account or money market fund',
            'suitable_for': ['emergency_fund', 'short_term', 'stability'],
            'allocation': cash_budget,
            'rationale': 'Cash reserve for emergencies and short-term needs'
        })
    
    # Verify total allocation sums to 100%
    total_alloc = sum(etf['allocation'] for etf in portfolio)
    if total_alloc != 100:
        # Normalize all allocations to sum to 100
        scale = 100 / total_alloc if total_alloc > 0 else 1
        for etf in portfolio:
            etf['allocation'] = round(etf['allocation'] * scale, 1)
        # Adjust last item to ensure exact 100%
        if portfolio:
            current_total = sum(etf['allocation'] for etf in portfolio)
            portfolio[-1]['allocation'] += (100 - current_total)
    
    return portfolio


def _fetch_etf_internal(symbol: str) -> Optional[Dict[str, Any]]:
    """Internal function to fetch ETF data."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=10)
    data = response.json()
    
    if "Global Quote" in data and data["Global Quote"]:
        quote = data["Global Quote"]
        return {
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "0%"),
        }
    return None


def fetch_etf_performance(symbol: str, user_id: str = "default") -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Fetch ETF performance data from Alpha Vantage with rate limiting.
    
    Args:
        symbol: ETF ticker symbol
        user_id: User identifier for rate limiting
        
    Returns:
        Tuple of (performance_data, status_message)
    """
    if RATE_LIMITER:
        cache_key = f"etf:{symbol}"
        
        result, from_cache, message = RATE_LIMITER.rate_limited_call(
            lambda: _fetch_etf_internal(symbol),
            cache_key,
            user_id
        )
        
        if result is None and "Rate limit" in message:
            return None, message
        
        status = "Cached" if from_cache else format_rate_limit_status(RATE_LIMITER, user_id)
        return result, status
    else:
        try:
            result = _fetch_etf_internal(symbol)
            return result, ""
        except:
            return None, "Error"


def render_etf_card(etf: Dict[str, Any], show_live_data: bool = True, user_id: str = "default") -> str:
    """
    Render an ETF recommendation card.
    
    Returns:
        Rate limit status message
    """
    symbol = etf['symbol']
    allocation = etf.get('allocation', 0)
    
    # Fetch live price if enabled (skip for CASH)
    live_data = None
    rate_status = ""
    if show_live_data and symbol != 'CASH':
        live_data, rate_status = fetch_etf_performance(symbol, user_id)
    
    # Card styling
    risk_colors = {
        'low': '#4CAF50',
        'moderate_low': '#8BC34A',
        'moderate': '#FFC107',
        'moderate_high': '#FF9800',
        'high': '#FF5722',
        'very_high': '#F44336',
    }
    risk_color = risk_colors.get(etf.get('risk_level', 'moderate'), '#FFC107')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid {risk_color};
    ">
        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
                <span style="color: #fff; font-size: 1.3em; font-weight: bold;">{symbol}</span>
                <span style="
                    background: {risk_color}33;
                    color: {risk_color};
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 0.7em;
                    margin-left: 8px;
                ">{etf['risk_level'].replace('_', ' ').title()}</span>
            </div>
            <div style="text-align: right;">
                <div style="color: #2E86AB; font-size: 1.4em; font-weight: bold;">{allocation}%</div>
                <div style="color: #888; font-size: 0.8em;">of portfolio</div>
            </div>
        </div>
        <div style="color: #ccc; margin-top: 4px; font-size: 0.95em;">{etf['name']}</div>
        <div style="color: #888; margin-top: 8px; font-size: 0.85em;">{etf['description']}</div>
        <div style="margin-top: 12px; display: flex; gap: 16px; color: #aaa; font-size: 0.8em;">
            <span>📊 {etf['category']}</span>
            <span>💰 ER: {etf['expense_ratio']:.2f}%</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Live data badge
    if live_data:
        change_color = "#4CAF50" if live_data['change'] >= 0 else "#F44336"
        st.markdown(f"""
        <div style="
            background: #0a0a15;
            padding: 8px 12px;
            border-radius: 0 0 8px 8px;
            margin-top: -8px;
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
        ">
            <span style="color: #fff;">Current: ${live_data['price']:.2f}</span>
            <span style="color: {change_color};">
                {'▲' if live_data['change'] >= 0 else '▼'} {live_data['change_percent']}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    # Rationale
    if etf.get('rationale'):
        st.caption(f"💡 {etf['rationale']}")
    
    return rate_status


def render_portfolio_summary(portfolio: List[Dict[str, Any]], savings: float) -> None:
    """Render portfolio summary with dollar amounts."""
    
    st.subheader("💵 Your Recommended Portfolio")
    
    total_expense = sum(etf['expense_ratio'] * etf['allocation'] / 100 for etf in portfolio)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Portfolio", f"${savings:,.0f}")
    
    with col2:
        st.metric(
            "Weighted Expense Ratio",
            f"{total_expense:.3f}%",
            help="Lower is better. Under 0.20% is excellent."
        )
    
    with col3:
        annual_cost = savings * total_expense / 100
        st.metric(
            "Annual Fees",
            f"${annual_cost:,.0f}",
            help="Estimated annual cost in fees"
        )
    
    st.divider()
    
    # Allocation breakdown
    for etf in portfolio:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{etf['symbol']}** - {etf['name']}")
        with col2:
            st.write(f"{etf['allocation']}%")
        with col3:
            amount = savings * etf['allocation'] / 100
            st.write(f"${amount:,.0f}")


def render_investment_recommendations(
    profile: Optional[Dict[str, Any]],
    recommendation: Optional[Dict[str, Any]]
) -> None:
    """Main investment recommendations component."""
    
    st.header("💼 Personalized Investment Recommendations")
    
    if not profile or not recommendation:
        st.warning("Please create or select a session to get personalized investment recommendations.")
        return
    
    st.markdown(f"""
    Based on your profile:
    - **Risk Tolerance:** {profile.get('risk_tolerance', 'Moderate')}
    - **Investment Horizon:** {profile.get('investment_horizon_years', 10)} years
    - **Goals:** {', '.join(profile.get('financial_goals', ['Retirement']))}
    """)
    
    st.divider()
    
    # Build recommendations (cached in session state for performance)
    cache_key = f"portfolio_{profile.get('risk_tolerance')}_{profile.get('investment_horizon_years')}"
    if cache_key not in st.session_state or st.session_state.get('_portfolio_profile') != profile:
        portfolio = build_recommended_portfolio(profile, recommendation)
        st.session_state[cache_key] = portfolio
        st.session_state['_portfolio_profile'] = profile.copy()
    else:
        portfolio = st.session_state[cache_key]
    
    savings = float(profile.get('savings', 10000))
    
    # Summary
    render_portfolio_summary(portfolio, savings)
    
    st.divider()
    
    # Settings
    col1, col2 = st.columns([3, 1])
    with col1:
        # Show rate limit status
        if RATE_LIMITER:
            status = format_rate_limit_status(RATE_LIMITER)
            if "Rate limit" in status:
                st.warning(status)
            else:
                st.caption(status)
    with col2:
        show_live = st.checkbox("Show live prices", value=True)
    
    # Individual recommendations
    st.subheader("📋 Recommended ETFs")
    
    # Limit live data fetching to first 3 ETFs to avoid rate limiting
    for i, etf in enumerate(portfolio):
        show_live_for_etf = show_live and i < 3  # Only fetch live for first 3
        render_etf_card(etf, show_live_data=show_live_for_etf)
        st.write("")  # Spacing
    
    # Disclaimer
    st.divider()
    st.info("""
    ⚠️ **Important Disclaimer:**
    These recommendations are for educational purposes only and should not be considered financial advice.
    Please consult a licensed financial advisor before making investment decisions.
    Past performance does not guarantee future results.
    """)
    
    # Additional context
    with st.expander("📚 How These Recommendations Were Made"):
        st.markdown(f"""
        **Your Profile Analysis:**
        
        1. **Risk Assessment**: Your {profile.get('risk_tolerance', 'Moderate')} risk tolerance 
           suggests a {'higher allocation to growth assets' if profile.get('risk_tolerance') in ['High', 'Very High'] else 'balanced approach with stability focus'}.
        
        2. **Time Horizon**: With {profile.get('investment_horizon_years', 10)} years to invest,
           you {'can afford more volatility for higher potential returns' if profile.get('investment_horizon_years', 10) > 10 else 'should consider a mix of growth and stability'}.
        
        3. **Goal Alignment**: Your goals ({', '.join(profile.get('financial_goals', ['Retirement']))})
           have been factored into the sector and style recommendations.
        
        4. **Target Allocation**: We've matched ETFs to your target allocation of
           {recommendation.get('target_allocation', {}).get('stocks', 60)}% stocks / 
           {recommendation.get('target_allocation', {}).get('bonds', 30)}% bonds.
        
        **Selection Criteria:**
        - Low expense ratios (preferring under 0.10%)
        - High liquidity and trading volume
        - Strong track record and AUM
        - Diversification benefits
        """)

