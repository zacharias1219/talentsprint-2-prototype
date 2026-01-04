"""
Stock Price Card Component.

Detects stock symbols in queries and displays real-time price data.
Includes rate limiting to protect Alpha Vantage API quota.
"""

import streamlit as st
import requests
import re
import os
import sys
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Add src to path for rate limiter import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

# Import rate limiter
try:
    from utils.rate_limiter import get_alpha_vantage_limiter, format_rate_limit_status, RateLimitExceeded
    RATE_LIMITER_AVAILABLE = True
except ImportError:
    RATE_LIMITER_AVAILABLE = False

# Common stock symbols for detection
COMMON_STOCKS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "GOOG": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla Inc.",
    "NVDA": "NVIDIA Corp.",
    "JPM": "JPMorgan Chase",
    "V": "Visa Inc.",
    "JNJ": "Johnson & Johnson",
    "WMT": "Walmart Inc.",
    "PG": "Procter & Gamble",
    "MA": "Mastercard Inc.",
    "UNH": "UnitedHealth Group",
    "HD": "Home Depot",
    "DIS": "Walt Disney Co.",
    "BAC": "Bank of America",
    "NFLX": "Netflix Inc.",
    "VZ": "Verizon",
    "INTC": "Intel Corp.",
    "AMD": "AMD Inc.",
    "CRM": "Salesforce",
    "PYPL": "PayPal Holdings",
    "COST": "Costco",
    "PEP": "PepsiCo",
    "KO": "Coca-Cola",
    "MRK": "Merck & Co.",
    "ABT": "Abbott Labs",
    "TMO": "Thermo Fisher",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
    "VTI": "Vanguard Total Market ETF",
    "VOO": "Vanguard S&P 500 ETF",
    "IWM": "iShares Russell 2000 ETF",
}


def detect_stock_symbols(text: str) -> List[str]:
    """
    Detect stock symbols in text.
    
    Patterns:
    - $AAPL (with dollar sign)
    - AAPL (uppercase, 1-5 chars, standalone word)
    - "Apple stock", "Microsoft shares" (company name references)
    
    Args:
        text: User query text
        
    Returns:
        List of detected stock symbols (uppercase)
    """
    symbols = set()
    
    # Pattern 1: $SYMBOL format
    dollar_pattern = r'\$([A-Z]{1,5})\b'
    matches = re.findall(dollar_pattern, text.upper())
    symbols.update(matches)
    
    # Pattern 2: Check for known symbols as standalone words
    words = re.findall(r'\b([A-Z]{1,5})\b', text.upper())
    for word in words:
        if word in COMMON_STOCKS:
            symbols.add(word)
    
    # Pattern 3: Company name mentions
    text_lower = text.lower()
    company_to_symbol = {
        "apple": "AAPL",
        "microsoft": "MSFT", 
        "google": "GOOGL",
        "amazon": "AMZN",
        "meta": "META",
        "facebook": "META",
        "tesla": "TSLA",
        "nvidia": "NVDA",
        "netflix": "NFLX",
        "disney": "DIS",
        "intel": "INTC",
        "amd": "AMD",
        "paypal": "PYPL",
        "salesforce": "CRM",
        "coca-cola": "KO",
        "coca cola": "KO",
        "pepsi": "PEP",
        "walmart": "WMT",
        "costco": "COST",
    }
    
    for company, symbol in company_to_symbol.items():
        if company in text_lower:
            symbols.add(symbol)
    
    return list(symbols)


def _fetch_quote_internal(symbol: str) -> Optional[Dict[str, Any]]:
    """Internal function to fetch quote (used by rate limiter)."""
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
            "symbol": quote.get("01. symbol", symbol),
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("09. change", 0)),
            "change_percent": quote.get("10. change percent", "0%").replace("%", ""),
            "high": float(quote.get("03. high", 0)),
            "low": float(quote.get("04. low", 0)),
            "volume": int(quote.get("06. volume", 0)),
            "previous_close": float(quote.get("08. previous close", 0)),
            "timestamp": datetime.now().isoformat(),
            "source": "Alpha Vantage"
        }
    
    return None


def fetch_stock_quote(symbol: str, user_id: str = "default") -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Fetch real-time stock quote from Alpha Vantage with rate limiting.
    
    Args:
        symbol: Stock ticker symbol
        user_id: User identifier for rate limiting
        
    Returns:
        Tuple of (quote_data, status_message)
    """
    if RATE_LIMITER_AVAILABLE:
        limiter = get_alpha_vantage_limiter()
        cache_key = f"quote:{symbol}"
        
        # Try with rate limiting
        result, from_cache, message = limiter.rate_limited_call(
            lambda: _fetch_quote_internal(symbol),
            cache_key,
            user_id
        )
        
        if result is None and "Rate limit" in message:
            return None, message
        
        status = "📦 Cached" if from_cache else format_rate_limit_status(limiter, user_id)
        return result, status
    else:
        # Fallback without rate limiting
        try:
            result = _fetch_quote_internal(symbol)
            return result, "No rate limiting"
        except Exception as e:
            return None, f"Error: {e}"


def get_mock_quote(symbol: str) -> Dict[str, Any]:
    """Generate mock quote data for demo purposes."""
    import random
    
    base_prices = {
        "AAPL": 185.50, "MSFT": 378.20, "GOOGL": 141.80, "AMZN": 178.90,
        "META": 505.30, "TSLA": 248.50, "NVDA": 495.20, "NFLX": 628.40,
        "JPM": 198.60, "V": 279.30, "SPY": 478.50, "QQQ": 408.70,
    }
    
    base_price = base_prices.get(symbol, 150.00)
    change = random.uniform(-5, 5)
    
    return {
        "symbol": symbol,
        "price": round(base_price + change, 2),
        "change": round(change, 2),
        "change_percent": round((change / base_price) * 100, 2),
        "high": round(base_price + abs(change) + 2, 2),
        "low": round(base_price - abs(change) - 2, 2),
        "volume": random.randint(10000000, 100000000),
        "previous_close": round(base_price, 2),
        "timestamp": datetime.now().isoformat(),
        "source": "Demo Data"
    }


def render_stock_card(quote: Dict[str, Any]) -> None:
    """
    Render a stock price card in Streamlit.
    
    Args:
        quote: Quote data dictionary
    """
    symbol = quote["symbol"]
    company_name = COMMON_STOCKS.get(symbol, symbol)
    price = quote["price"]
    change = quote["change"]
    change_pct = float(quote["change_percent"])
    
    # Determine color
    is_positive = change >= 0
    color = "#00C853" if is_positive else "#FF1744"
    arrow = "▲" if is_positive else "▼"
    sign = "+" if is_positive else ""
    
    # Card HTML/CSS
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 16px 20px;
        margin: 10px 0;
        border-left: 4px solid {color};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="color: #fff; font-size: 1.4em; font-weight: bold;">{symbol}</span>
                <span style="color: #888; font-size: 0.9em; margin-left: 8px;">{company_name}</span>
            </div>
            <div style="text-align: right;">
                <div style="color: #fff; font-size: 1.5em; font-weight: bold;">${price:,.2f}</div>
                <div style="color: {color}; font-size: 1em;">
                    {arrow} {sign}{change:,.2f} ({sign}{change_pct:.2f}%)
                </div>
            </div>
        </div>
        <div style="margin-top: 12px; display: flex; gap: 20px; color: #aaa; font-size: 0.85em;">
            <span>High: ${quote['high']:,.2f}</span>
            <span>Low: ${quote['low']:,.2f}</span>
            <span>Vol: {quote['volume']:,}</span>
        </div>
        <div style="margin-top: 8px; color: #666; font-size: 0.75em;">
            {quote['source']} - {quote['timestamp'][:19]}
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_stock_context_for_chat(
    symbols: List[str], 
    user_id: str = "default"
) -> Tuple[str, List[Dict[str, Any]], str]:
    """
    Get stock data to include in chat context.
    
    Args:
        symbols: List of stock symbols to fetch
        user_id: User identifier for rate limiting
        
    Returns:
        Tuple of (context_string, list_of_quotes, rate_limit_status)
    """
    quotes = []
    context_parts = []
    status_messages = []
    
    for symbol in symbols[:3]:  # Limit to 3 stocks per query
        quote, status = fetch_stock_quote(symbol, user_id)
        status_messages.append(status)
        
        if quote is None:
            # Use mock data if API fails or rate limited
            quote = get_mock_quote(symbol)
            quote["source"] = "Demo (rate limited)" if "Rate limit" in status else "Demo"
        
        quotes.append(quote)
        
        company = COMMON_STOCKS.get(symbol, symbol)
        change_str = f"+{quote['change']}" if quote['change'] >= 0 else str(quote['change'])
        
        context_parts.append(
            f"{symbol} ({company}): ${quote['price']:.2f} ({change_str}, {quote['change_percent']}%)"
        )
    
    context_string = "\n".join([
        "\nReal-Time Stock Data:",
        *context_parts,
        ""
    ]) if context_parts else ""
    
    # Use the most informative status message
    final_status = status_messages[-1] if status_messages else ""
    
    return context_string, quotes, final_status


def render_stock_cards_for_query(query: str, user_id: str = "default") -> Tuple[str, bool]:
    """
    Detect stocks in query and render price cards.
    
    Args:
        query: User's chat query
        user_id: User identifier for rate limiting
        
    Returns:
        Tuple of (context_to_add, cards_shown)
    """
    symbols = detect_stock_symbols(query)
    
    if not symbols:
        return "", False
    
    context_str, quotes, rate_status = get_stock_context_for_chat(symbols, user_id)
    
    if quotes:
        st.markdown("**📊 Live Market Data:**")
        
        # Show rate limit status
        if rate_status:
            if "Rate limit" in rate_status:
                st.warning(rate_status)
            else:
                st.caption(rate_status)
        
        for quote in quotes:
            render_stock_card(quote)
    
    return context_str, len(quotes) > 0

