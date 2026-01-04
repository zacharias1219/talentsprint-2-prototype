# Alpha Vantage API Setup Guide

## Overview

The Financial Advisor app uses Alpha Vantage API to fetch real-time and historical market data. This document explains what's needed to connect and display accurate data.

## What Data We Fetch

### 1. **Real-Time Stock Quotes** (`GLOBAL_QUOTE`)
- Current price
- Daily change (amount and percentage)
- Volume
- High/Low for the day
- Open and previous close

**Used in:** Market Overview section

### 2. **Historical Daily Prices** (`TIME_SERIES_DAILY`)
- Open, High, Low, Close (OHLC) prices
- Volume
- Up to 100 days (compact) or full history (full)

**Used in:** Stock price charts (candlestick)

### 3. **Technical Indicators** (`RSI`)
- Relative Strength Index (14-day)
- Overbought/Oversold signals

**Used in:** RSI indicator chart

### 4. **News & Sentiment** (`NEWS_SENTIMENT`)
- Financial news articles
- Sentiment scores (positive/negative/neutral)
- Article summaries

**Used in:** News section with sentiment analysis

## Setup Steps

### 1. Get API Key

1. Go to https://www.alphavantage.co/support/#api-key
2. Fill out the form (name, email)
3. You'll receive a free API key via email
4. **Free tier limits:**
   - 5 API calls per minute
   - 500 calls per day

### 2. Add to Environment

Create or edit `.env` file in project root:

```bash
ALPHA_VANTAGE_API_KEY=your_actual_api_key_here
```

**Important:** Never commit your API key to git! The `.env` file should be in `.gitignore`.

### 3. Verify Connection

1. Run the app: `python run_app.py ui`
2. Go to "Market Data" tab
3. You should see: **🟢 Live Data - Connected to Alpha Vantage API**

## How It Works

### Caching System

To respect rate limits, we use **Streamlit caching**:
- Data is cached for **60 seconds**
- Reduces API calls when multiple users view the same symbol
- Cache automatically refreshes after 60s

### Rate Limiting

Alpha Vantage free tier: **5 calls/minute**

**Our implementation:**
- Uses `@st.cache_data(ttl=60)` to cache responses
- Shows rate limit warnings if exceeded
- Falls back to mock data if API fails

### Error Handling

The app handles:
- ✅ **Network errors** - Shows user-friendly message
- ✅ **Rate limits** - Warns user, suggests waiting
- ✅ **Invalid symbols** - Shows error, falls back to mock
- ✅ **API errors** - Displays specific error message
- ✅ **Missing API key** - Uses demo mode automatically

## API Endpoints Used

| Endpoint | Function | Purpose | Rate Limit Impact |
|----------|----------|---------|-------------------|
| `GLOBAL_QUOTE` | Real-time quote | Current price, change | 1 call per symbol |
| `TIME_SERIES_DAILY` | Historical prices | Price charts | 1 call per symbol |
| `RSI` | Technical indicator | RSI chart | 1 call per symbol |
| `NEWS_SENTIMENT` | News articles | News feed | 1 call per symbol |

## Data Flow

```
User opens Market Data tab
    ↓
Check if API_KEY exists in .env
    ↓
If yes: Fetch from Alpha Vantage API
    ↓
Cache response for 60 seconds
    ↓
Display in UI (charts, metrics, news)
    ↓
If API fails: Show error + use mock data
```

## Troubleshooting

### "Demo Mode" shown instead of "Live Data"

**Cause:** API key not found or invalid

**Fix:**
1. Check `.env` file exists in project root
2. Verify `ALPHA_VANTAGE_API_KEY=your_key` is set
3. Restart the Streamlit app
4. Check for typos in the key

### "Rate limit reached" warning

**Cause:** Too many API calls (free tier = 5/min)

**Fix:**
1. Wait 1 minute before refreshing
2. The cache will serve data for 60 seconds
3. Consider upgrading to premium tier for higher limits

### "API Error: Invalid API call"

**Cause:** Invalid function name or parameters

**Fix:**
- This shouldn't happen with our code
- Check Alpha Vantage status: https://www.alphavantage.co/support/
- Verify your API key is active

### No data showing

**Cause:** API response format changed or network issue

**Fix:**
1. Check internet connection
2. Verify API key is valid (test at https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY)
3. Check browser console for errors
4. App will automatically fall back to mock data

## Testing API Connection

Test your API key manually:

```bash
# Replace YOUR_KEY with your actual key
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY"
```

Expected response:
```json
{
  "Global Quote": {
    "01. symbol": "AAPL",
    "05. price": "185.60",
    "09. change": "2.30",
    ...
  }
}
```

## Premium Tier (Optional)

For production use, consider upgrading:
- **75 calls/minute** - $49.99/month
- **120 calls/minute** - $149.99/month
- **Unlimited** - Custom pricing

Benefits:
- Higher rate limits
- Priority support
- More reliable service

## Code Structure

### Key Files

1. **`ui/components/market_dashboard.py`**
   - Main dashboard component
   - API functions: `fetch_stock_quote()`, `fetch_daily_prices()`, etc.
   - UI rendering: `render_market_overview()`, `render_stock_chart()`, etc.

2. **`.env`**
   - Stores API key securely
   - Not committed to git

### Key Functions

```python
# Cached API call wrapper
@st.cache_data(ttl=60)
def _cached_api_call(function_name, symbol, **params)

# Fetch real-time quote
fetch_stock_quote(symbol: str) -> Dict

# Fetch historical prices
fetch_daily_prices(symbol: str, days: int) -> DataFrame

# Fetch RSI indicator
fetch_rsi(symbol: str) -> DataFrame

# Fetch news with sentiment
fetch_news(symbol: str) -> List[Dict]
```

## Best Practices

1. **Always cache API responses** - Reduces rate limit issues
2. **Handle errors gracefully** - Show user-friendly messages
3. **Fall back to mock data** - App works even without API
4. **Don't expose API keys** - Use `.env` file
5. **Monitor rate limits** - Track API usage
6. **Validate data** - Check for empty/null responses

## Summary

✅ **What you need:**
- Alpha Vantage API key (free)
- `.env` file with `ALPHA_VANTAGE_API_KEY=your_key`
- Internet connection

✅ **What the app does:**
- Automatically detects API key
- Fetches real market data
- Caches responses (60s) to respect rate limits
- Falls back to demo data if API unavailable
- Shows clear status indicators

✅ **What you get:**
- Real-time stock prices
- Historical price charts
- Technical indicators (RSI)
- Financial news with sentiment

---

**Last Updated:** 2025-01-XX
**API Version:** Alpha Vantage v1.0

