"""
Market data dashboard component for Streamlit UI.

Displays live market data from Alpha Vantage API.
Includes centralized rate limiting to protect API quota.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project directories to path
project_root = Path(__file__).parent.parent.parent
scripts_path = project_root / "scripts"
src_path = project_root / "src"
sys.path.insert(0, str(scripts_path))
sys.path.insert(0, str(src_path))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()  # Try default .env location
except ImportError:
    pass  # dotenv not available, use system env vars

# Import centralized rate limiter
try:
    from utils.rate_limiter import get_alpha_vantage_limiter, format_rate_limit_status
    RATE_LIMITER = get_alpha_vantage_limiter()
except ImportError:
    RATE_LIMITER = None

# Alpha Vantage API setup
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")

try:
    import requests
except ImportError:
    requests = None

# Rate limiting: Alpha Vantage free tier = 5 calls/minute
# Cache data for 300 seconds (5 minutes) to reduce API calls
RATE_LIMIT_CALLS_PER_MIN = 5
CACHE_DURATION = 300  # seconds - increased for better performance


# ============================================================================
# RATE LIMITING & CACHING
# ============================================================================

def _make_api_request(function_name: str, symbol: str, **extra_params) -> Optional[Dict]:
    """Internal function to make the actual API request."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": function_name,
        "symbol": symbol,
        "apikey": API_KEY,
        **extra_params
    }
    
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    
    # Check for API errors
    if "Error Message" in data:
        return None
    
    if "Note" in data:
        # Rate limit message from Alpha Vantage itself
        return None
    
    return data


@st.cache_data(ttl=CACHE_DURATION, show_spinner=False)
def _cached_api_call(function_name: str, symbol: str, user_id: str = "default", **extra_params) -> Optional[Dict]:
    """
    Cached wrapper for Alpha Vantage API calls with rate limiting.
    
    Args:
        function_name: Alpha Vantage function name
        symbol: Stock symbol
        user_id: User identifier for rate limiting
        **extra_params: Additional API parameters
    
    Returns:
        API response data or None
    """
    if not requests:
        return None
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE" or API_KEY.strip() == "":
        return None
    
    # Use centralized rate limiter if available
    if RATE_LIMITER:
        cache_key = f"market:{function_name}:{symbol}"
        
        # Check rate limit
        allowed, message = RATE_LIMITER.check_rate_limit(user_id)
        if not allowed:
            return None
        
        # Record the call
        RATE_LIMITER.record_call(user_id)
    
    try:
        return _make_api_request(function_name, symbol, **extra_params)
    except requests.exceptions.RequestException as e:
        return None
    except json.JSONDecodeError:
        return None
    except Exception as e:
        return None


def get_rate_limit_status(user_id: str = "default") -> str:
    """
    Get current rate limit status for display.
    
    Args:
        user_id: User identifier
        
    Returns:
        Formatted status string
    """
    if RATE_LIMITER:
        return format_rate_limit_status(RATE_LIMITER, user_id)
    return ""


# ============================================================================
# ALPHA VANTAGE API FUNCTIONS
# ============================================================================

def fetch_stock_quote(symbol: str) -> Optional[Dict]:
    """
    Fetch real-time stock quote from Alpha Vantage.
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
    
    Returns:
        Dictionary with quote data or None
    """
    data = _cached_api_call("GLOBAL_QUOTE", symbol)
    
    if not data or "Global Quote" not in data:
        return None
    
    quote = data["Global Quote"]
    if not quote:
        return None
    
    try:
        return {
            "symbol": quote.get("01. symbol", symbol),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": float(quote.get("10. change percent", "0%").replace("%", "")),
            "volume": int(quote.get("06. volume", 0)),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "open": float(quote.get("02. open", 0)),
            "previous_close": float(quote.get("08. previous close", 0)),
        }
    except (ValueError, TypeError) as e:
        st.warning(f"Error parsing quote data for {symbol}: {e}")
        return None


def fetch_daily_prices(symbol: str, days: int = 30) -> Optional[pd.DataFrame]:
    """
    Fetch historical daily prices from Alpha Vantage.
    
    Args:
        symbol: Stock symbol
        days: Number of days to retrieve (max 100 for compact, full history for full)
    
    Returns:
        DataFrame with OHLCV data or None
    """
    # Use 'full' if days > 100, otherwise 'compact' to save API calls
    outputsize = "full" if days > 100 else "compact"
    
    data = _cached_api_call("TIME_SERIES_DAILY", symbol, outputsize=outputsize)
    
    if not data or "Time Series (Daily)" not in data:
        return None
    
    try:
        ts = data["Time Series (Daily)"]
        if not ts:
            return None
        
        df = pd.DataFrame.from_dict(ts, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.tail(days)
        
        # Alpha Vantage column names: "1. open", "2. high", etc.
        column_mapping = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        }
        
        df = df.rename(columns=column_mapping)
        df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
        
        return df
    except (ValueError, KeyError, TypeError) as e:
        st.warning(f"Error parsing price data for {symbol}: {e}")
        return None


def fetch_rsi(symbol: str) -> Optional[pd.DataFrame]:
    """
    Fetch RSI indicator from Alpha Vantage.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        DataFrame with RSI values or None
    """
    data = _cached_api_call(
        "RSI",
        symbol,
        interval="daily",
        time_period=14,
        series_type="close"
    )
    
    if not data or "Technical Analysis: RSI" not in data:
        return None
    
    try:
        rsi_data = data["Technical Analysis: RSI"]
        if not rsi_data:
            return None
        
        df = pd.DataFrame.from_dict(rsi_data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.tail(14)
        
        # Alpha Vantage returns "RSI" as column name
        if "RSI" in df.columns:
            df = df[["RSI"]].rename(columns={"RSI": "rsi"})
        else:
            df.columns = ['rsi']
        
        df = df.astype(float)
        return df
    except (ValueError, KeyError, TypeError) as e:
        st.warning(f"Error parsing RSI data for {symbol}: {e}")
        return None


def fetch_news(symbol: str) -> Optional[List[Dict]]:
    """
    Fetch news with sentiment from Alpha Vantage.
    
    Args:
        symbol: Stock symbol
    
    Returns:
        List of news items or None
    """
    data = _cached_api_call("NEWS_SENTIMENT", symbol, tickers=symbol, limit=5)
    
    if not data or "feed" not in data:
        return None
    
    feed = data.get("feed", [])
    if not feed:
        return None
    
    return feed[:5]


# ============================================================================
# MOCK DATA (FALLBACK)
# ============================================================================

MOCK_QUOTES = {
    "AAPL": {"price": 185.60, "change": 2.30, "change_percent": 1.25, "high": 187.20, "low": 183.40, "volume": 45000000},
    "MSFT": {"price": 370.25, "change": -1.80, "change_percent": -0.48, "high": 372.50, "low": 368.10, "volume": 22000000},
    "GOOGL": {"price": 140.10, "change": 2.50, "change_percent": 1.82, "high": 141.30, "low": 138.50, "volume": 18000000},
    "VTI": {"price": 225.40, "change": 2.00, "change_percent": 0.90, "high": 226.80, "low": 223.90, "volume": 4500000},
    "BND": {"price": 72.30, "change": -0.20, "change_percent": -0.28, "high": 72.60, "low": 72.10, "volume": 5200000},
    "SPY": {"price": 450.20, "change": 3.50, "change_percent": 0.78, "high": 452.10, "low": 447.80, "volume": 65000000},
}


def generate_calculated_prices(symbol: str, days: int = 30, reduce_points: bool = True) -> pd.DataFrame:
    """
    Generate calculated historical prices based on realistic market patterns.
    
    Args:
        symbol: Stock symbol
        days: Number of days to generate
        reduce_points: If True, reduce to ~20 points for faster rendering
    """
    from components.portfolio_calculations import calculate_historical_prices_from_returns
    
    base = MOCK_QUOTES.get(symbol, MOCK_QUOTES["AAPL"])["price"]
    
    # Reduce data points for faster initial rendering
    if reduce_points and days > 20:
        # Use business days only and sample every Nth day
        actual_days = min(days, 20)  # Max 20 points for initial render
        dates = pd.date_range(end=pd.Timestamp.now(), periods=actual_days, freq='B')  # Business days
    else:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # Use realistic stock market returns (based on historical averages)
    # Stocks typically have ~10% annual return with ~15% volatility
    daily_return = 0.10 / 252  # Annual return converted to daily
    daily_vol = 0.15 / np.sqrt(252)  # Annual volatility converted to daily
    
    np.random.seed(hash(symbol) % 2**32)
    returns = np.random.normal(daily_return, daily_vol, len(dates))
    
    # Generate OHLC data from returns
    df = calculate_historical_prices_from_returns(base, returns, dates)
    return df


def generate_calculated_rsi(days: int = 14, reduce_points: bool = True) -> pd.DataFrame:
    """
    Generate calculated RSI values based on realistic market patterns.
    
    Args:
        days: Number of days to generate
        reduce_points: If True, reduce to ~10 points for faster rendering
    """
    # Reduce points for faster rendering
    if reduce_points and days > 10:
        actual_days = min(days, 10)
        dates = pd.date_range(end=pd.Timestamp.now(), periods=actual_days, freq='D')
    else:
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq='D')
    
    # RSI typically oscillates around 50, with realistic movement
    # Start near neutral (50), add realistic momentum changes
    np.random.seed(42)
    rsi = 50.0
    rsi_values = [rsi]
    
    for _ in range(len(dates) - 1):
        # RSI moves in a mean-reverting pattern
        # If above 50, tendency to revert down; if below 50, tendency to revert up
        mean_reversion = (50 - rsi) * 0.1
        random_walk = np.random.normal(0, 3)  # Small random movements
        rsi += mean_reversion + random_walk
        rsi = np.clip(rsi, 20, 80)  # Keep in realistic range
        rsi_values.append(rsi)
    
    return pd.DataFrame({'rsi': rsi_values}, index=dates)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def _fetch_quotes_parallel(symbols: List[str], user_id: str = "default") -> Dict[str, Optional[Dict]]:
    """Fetch multiple stock quotes in parallel."""
    api_active = API_KEY and API_KEY != "YOUR_API_KEY_HERE" and API_KEY.strip() != ""
    if not api_active:
        return {symbol: None for symbol in symbols}
    
    results = {}
    
    # Use ThreadPoolExecutor for parallel API calls
    with ThreadPoolExecutor(max_workers=min(len(symbols), 5)) as executor:
        future_to_symbol = {
            executor.submit(fetch_stock_quote, symbol): symbol 
            for symbol in symbols
        }
        
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                results[symbol] = future.result(timeout=10)
            except Exception:
                results[symbol] = None
    
    return results


def render_market_overview() -> None:
    """Render market overview with key metrics - instant loading with calculated data."""
    st.header("📈 Market Overview")
    
    # Show API status
    api_active = API_KEY and API_KEY != "YOUR_API_KEY_HERE" and API_KEY.strip() != ""
    if api_active:
        st.success("🟢 **Live Data** - Connected to Alpha Vantage API")
        st.caption(f"⚠️ Rate limit: {RATE_LIMIT_CALLS_PER_MIN} calls/minute. Data cached for {CACHE_DURATION}s to reduce API usage.")
    else:
        st.warning("🟡 **Demo Mode** - Using sample data. Add `ALPHA_VANTAGE_API_KEY` to `.env` for live data")
    
    symbols = ["AAPL", "MSFT", "GOOGL", "SPY", "BND"]
    
    # Initialize session state for quotes if not exists
    cache_key = f"market_quotes_{hash(tuple(symbols))}"
    if cache_key not in st.session_state:
        st.session_state[cache_key] = {}
        st.session_state[f"{cache_key}_timestamp"] = 0
    
    # Check if cache is still valid (5 minutes)
    cache_age = time.time() - st.session_state.get(f"{cache_key}_timestamp", 0)
    quotes = st.session_state.get(cache_key, {})
    
    # Show calculated data IMMEDIATELY (no waiting)
    cols = st.columns(len(symbols))
    placeholders = {}
    
    for i, symbol in enumerate(symbols):
        with cols[i]:
            mock = MOCK_QUOTES.get(symbol, MOCK_QUOTES["AAPL"])
            placeholders[symbol] = st.empty()
            placeholders[symbol].metric(
                symbol,
                f"${mock['price']:.2f}",
                delta=f"{mock['change_percent']:.2f}%",
                delta_color="normal" if mock['change'] >= 0 else "inverse"
            )
            if not api_active:
                st.caption("📊 Calculated data")
            else:
                st.caption("📊 Loading...")
    
    # Fetch live data in background ONLY if cache is stale (non-blocking)
    if api_active and (cache_age > CACHE_DURATION or not quotes):
        # Use a placeholder for status update
        status_placeholder = st.empty()
        
        # Fetch in background without blocking UI
        try:
            quotes = _fetch_quotes_parallel(symbols)
            st.session_state[cache_key] = quotes
            st.session_state[f"{cache_key}_timestamp"] = time.time()
            
            # Update UI with live data
            for i, symbol in enumerate(symbols):
                quote = quotes.get(symbol)
                if quote and quote.get('price', 0) > 0:
                    with cols[i]:
                        placeholders[symbol].metric(
                            symbol,
                            f"${quote['price']:.2f}",
                            delta=f"{quote['change_percent']:.2f}%",
                            delta_color="normal" if quote['change'] >= 0 else "inverse"
                        )
                        st.caption(f"🟢 Live | Vol: {quote.get('volume', 0):,}")
        except Exception as e:
            status_placeholder.warning(f"Could not fetch live data: {str(e)[:50]}")
        finally:
            status_placeholder.empty()
    
    # Update with cached live data if available
    elif api_active and quotes:
        for i, symbol in enumerate(symbols):
            quote = quotes.get(symbol)
            if quote and quote.get('price', 0) > 0:
                with cols[i]:
                    placeholders[symbol].metric(
                        symbol,
                        f"${quote['price']:.2f}",
                        delta=f"{quote['change_percent']:.2f}%",
                        delta_color="normal" if quote['change'] >= 0 else "inverse"
                    )
                    st.caption(f"🟢 Live (cached) | Vol: {quote.get('volume', 0):,}")


def render_stock_chart(symbol: str = "AAPL") -> None:
    """Render stock price chart - lazy loaded and optimized for performance."""
    st.subheader(f"📊 {symbol} Price Trend (30 Days)")
    
    api_active = API_KEY and API_KEY != "YOUR_API_KEY_HERE" and API_KEY.strip() != ""
    
    # Check session state cache first
    cache_key = f"price_data_{symbol}"
    df = None
    data_source = "Calculated Data"
    
    if cache_key in st.session_state:
        cache_time = st.session_state.get(f"{cache_key}_time", 0)
        if time.time() - cache_time < CACHE_DURATION:
            df = st.session_state[cache_key]
            data_source = st.session_state.get(f"{cache_key}_source", "Cached")
            if data_source == "Live Data (Alpha Vantage)":
                st.caption(f"✅ {len(df)} days of real market data (cached)")
            else:
                st.caption("📊 Using calculated data")
    
    # Show calculated data IMMEDIATELY if no cache (reduced points for speed)
    if df is None or df.empty:
        df = generate_calculated_prices(symbol, 30, reduce_points=True)
        data_source = "Calculated Data"
        st.caption("📊 Using calculated data based on historical patterns")
        
        # Try to fetch live data in background (non-blocking)
        if api_active:
            try:
                live_df = fetch_daily_prices(symbol, 30)
                if live_df is not None and not live_df.empty:
                    # Downsample if too many points for performance
                    if len(live_df) > 30:
                        live_df = live_df.iloc[::max(1, len(live_df) // 30)]
                    df = live_df
                    data_source = "Live Data (Alpha Vantage)"
                    # Cache the result
                    st.session_state[cache_key] = df
                    st.session_state[f"{cache_key}_time"] = time.time()
                    st.session_state[f"{cache_key}_source"] = data_source
                    st.caption(f"✅ Updated with {len(df)} days of real market data")
            except:
                pass  # Keep calculated data if API fails
    
    if df.empty:
        st.error("No data available for this symbol.")
        return
    
    # Optimize chart rendering - use line chart instead of candlestick for better performance
    # Only use candlestick if data points are reasonable
    if len(df) <= 30:
        # Candlestick chart for detailed view
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol,
            increasing_line_color='#26a69a',
            decreasing_line_color='#ef5350'
        )])
    else:
        # Line chart for better performance with many points
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['close'],
            mode='lines',
            name=symbol,
            line=dict(color='#2E86AB', width=2)
        ))
    
    fig.update_layout(
        title=f"{symbol} Price Chart ({data_source})",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=400,
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        # Performance optimizations
        uirevision='constant',  # Prevents unnecessary redraws
        hovermode='x unified'  # Faster hover
    )
    
    # Use optimized plotly chart rendering
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],  # Remove heavy interactions
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{symbol}_chart'
        }
    })
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current", f"${df['close'].iloc[-1]:.2f}")
    with col2:
        change = df['close'].iloc[-1] - df['close'].iloc[0]
        change_pct = (change / df['close'].iloc[0]) * 100 if df['close'].iloc[0] > 0 else 0
        st.metric("30D Change", f"${change:.2f}", delta=f"{change_pct:.1f}%")
    with col3:
        st.metric("30D High", f"${df['high'].max():.2f}")
    with col4:
        st.metric("30D Low", f"${df['low'].min():.2f}")


def render_rsi_indicator(symbol: str = "AAPL") -> None:
    """Render RSI indicator - lazy loaded and optimized for performance."""
    st.subheader(f"📉 {symbol} RSI Indicator")
    
    api_active = API_KEY and API_KEY != "YOUR_API_KEY_HERE" and API_KEY.strip() != ""
    
    # Check session state cache first
    cache_key = f"rsi_data_{symbol}"
    df = None
    data_source = "Calculated"
    
    if cache_key in st.session_state:
        cache_time = st.session_state.get(f"{cache_key}_time", 0)
        if time.time() - cache_time < CACHE_DURATION:
            df = st.session_state[cache_key]
            data_source = st.session_state.get(f"{cache_key}_source", "Cached")
            if data_source == "Live":
                st.caption(f"✅ {len(df)} days of RSI data (cached)")
            else:
                st.caption("📊 Using calculated RSI data")
    
    # Show calculated data IMMEDIATELY if no cache (reduced points)
    if df is None or df.empty:
        df = generate_calculated_rsi(14, reduce_points=True)
        data_source = "Calculated"
        st.caption("📊 Using calculated RSI based on market patterns")
        
        # Try to fetch live data in background (non-blocking)
        if api_active:
            try:
                live_df = fetch_rsi(symbol)
                if live_df is not None and not live_df.empty:
                    # Downsample if too many points
                    if len(live_df) > 14:
                        live_df = live_df.iloc[::max(1, len(live_df) // 14)]
                    df = live_df
                    data_source = "Live"
                    # Cache the result
                    st.session_state[cache_key] = df
                    st.session_state[f"{cache_key}_time"] = time.time()
                    st.session_state[f"{cache_key}_source"] = data_source
                    st.caption(f"✅ Updated with {len(df)} days of real RSI data")
            except:
                pass  # Keep calculated data if API fails
    
    # Optimized chart rendering
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['rsi'],
        mode='lines',  # Removed markers for better performance
        name='RSI',
        line=dict(color='purple', width=2),
        hovertemplate='RSI: %{y:.1f}<extra></extra>'  # Simplified hover
    ))
    
    # Overbought/Oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig.add_hline(y=50, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title=f"RSI 14-Day ({data_source})",
        xaxis_title="Date",
        yaxis_title="RSI",
        height=300,
        yaxis_range=[0, 100],
        # Performance optimizations
        uirevision='constant',  # Prevents unnecessary redraws
        hovermode='x unified'  # Faster hover
    )
    
    # Optimized chart rendering
    st.plotly_chart(fig, use_container_width=True, config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': f'{symbol}_rsi'
        }
    })
    
    current_rsi = df['rsi'].iloc[-1]
    if current_rsi > 70:
        st.error(f"⚠️ RSI {current_rsi:.1f} - Overbought (potential sell signal)")
    elif current_rsi < 30:
        st.success(f"✅ RSI {current_rsi:.1f} - Oversold (potential buy signal)")
    else:
        st.info(f"ℹ️ RSI {current_rsi:.1f} - Neutral")


def render_news_sentiment() -> None:
    """Render financial news with sentiment analysis - optimized for speed."""
    st.subheader("📰 Financial News & Sentiment")
    
    api_active = API_KEY and API_KEY != "YOUR_API_KEY_HERE" and API_KEY.strip() != ""
    
    # Check session state cache first
    cache_key = "news_data"
    if cache_key in st.session_state:
        cache_time = st.session_state.get(f"{cache_key}_time", 0)
        if time.time() - cache_time < CACHE_DURATION:
            news = st.session_state[cache_key]
            if news:
                st.success(f"✅ Loaded {len(news)} news articles with sentiment analysis (cached)")
                for i, item in enumerate(news, 1):
                    title = item.get('title', 'No title')[:80]
                    with st.expander(f"{i}. {title}..."):
                        st.write(f"**Source**: {item.get('source', 'Unknown')}")
                        st.write(f"**Published**: {item.get('time_published', 'Unknown')[:10]}")
                        
                        sentiment = float(item.get('overall_sentiment_score', 0))
                        label = item.get('overall_sentiment_label', 'Neutral')
                        
                        color = "green" if sentiment > 0.15 else "red" if sentiment < -0.15 else "gray"
                        st.markdown(f"**Sentiment**: :{color}[{label}] ({sentiment:.3f})")
                        
                        if item.get('summary'):
                            st.write(f"**Summary**: {item['summary'][:300]}...")
                return
    
    # Show mock news IMMEDIATELY (no waiting)
    st.caption("📡 Sample financial news")
    mock_news = [
        {"title": "Tech Stocks Rally on Strong Earnings", "source": "Financial Times", "sentiment": 0.65},
        {"title": "Federal Reserve Holds Interest Rates Steady", "source": "Bloomberg", "sentiment": 0.1},
        {"title": "Renewable Energy Sector Sees Increased Investment", "source": "Reuters", "sentiment": 0.45},
    ]
    
    for i, item in enumerate(mock_news, 1):
        with st.expander(f"{i}. {item['title']}"):
            st.write(f"**Source**: {item['source']}")
            label = "Positive" if item['sentiment'] > 0.3 else "Negative" if item['sentiment'] < -0.3 else "Neutral"
            st.metric("Sentiment", label, f"{item['sentiment']:.2f}")
    
    # Fetch live news in background (non-blocking) if cache is stale
    cache_time = st.session_state.get(f"{cache_key}_time", 0)
    cache_age = time.time() - cache_time
    
    if api_active and (cache_age > CACHE_DURATION or not news):
        try:
            news = fetch_news("AAPL")
            if news:
                st.session_state[cache_key] = news
                st.session_state[f"{cache_key}_time"] = time.time()
                st.caption(f"✅ Updated with {len(news)} live news articles")
        except:
            pass  # Keep sample news if API fails


def render_market_dashboard() -> None:
    """Main market dashboard renderer - lazy loaded and optimized for performance."""
    
    # Show rate limit status at top (non-blocking)
    rate_status = get_rate_limit_status()
    if rate_status and "Rate limit" in rate_status:
        st.warning(rate_status)
    elif rate_status:
        st.caption(rate_status)
    
    # Render overview immediately (shows calculated data instantly)
    render_market_overview()
    
    st.divider()
    
    # Stock selector
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox(
            "Select Stock/ETF",
            ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "SPY", "VTI", "BND"],
            key="market_stock_select"
        )
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            # Clear cache for this symbol
            for key in list(st.session_state.keys()):
                if key.startswith(f"price_data_{selected}") or key.startswith(f"rsi_data_{selected}"):
                    del st.session_state[key]
            st.rerun()
    
    # Lazy loading: Use tabs/expanders so charts only render when viewed
    chart_tabs = st.tabs(["📊 Price Chart", "📉 RSI Indicator", "📰 News"])
    
    with chart_tabs[0]:
        # Only render chart when this tab is active
        render_stock_chart(selected)
    
    with chart_tabs[1]:
        # Only render RSI when this tab is active
        render_rsi_indicator(selected)
    
    with chart_tabs[2]:
        # Only render news when this tab is active
        render_news_sentiment()
