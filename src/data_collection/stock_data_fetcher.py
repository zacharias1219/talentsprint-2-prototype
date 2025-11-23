"""
Stock data fetcher module.

Fetches real-time and historical stock data using Alpha Vantage API.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from src.data_collection.alpha_vantage_client import AlphaVantageClient
from src.data_collection.cache_manager import CacheManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class StockDataFetcher:
    """Fetcher for stock market data."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize stock data fetcher.

        Args:
            cache_manager: Optional cache manager instance.
        """
        self.client = AlphaVantageClient()
        self.cache = cache_manager or CacheManager()

    def fetch_daily_data(
        self,
        symbol: str,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch daily stock data.

        Args:
            symbol: Stock symbol (e.g., 'AAPL').
            use_cache: Whether to use cached data if available.

        Returns:
            DataFrame with columns: date, open, high, low, close, volume.
        """
        cache_key = f"daily_{symbol}"

        # Check cache
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached daily data for {symbol}")
                return pd.DataFrame(cached_data)

        # Fetch from API
        try:
            result = self.client.get_daily_data(symbol=symbol, outputsize="full")
            data = result["data"]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = [col.split(" ")[1].lower() for col in df.columns]
            df = df.astype(float)
            df = df.sort_index()

            # Cache the data
            if use_cache:
                self.cache.set(cache_key, df.to_dict(orient="index"))

            logger.info(f"Fetched daily data for {symbol}: {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch daily data for {symbol}: {e}")
            raise

    def fetch_intraday_data(
        self,
        symbol: str,
        interval: str = "5min",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Fetch intraday stock data.

        Args:
            symbol: Stock symbol.
            interval: Time interval ('1min', '5min', '15min', '30min', '60min').
            use_cache: Whether to use cached data.

        Returns:
            DataFrame with intraday data.
        """
        cache_key = f"intraday_{symbol}_{interval}"

        # Check cache
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached intraday data for {symbol}")
                return pd.DataFrame(cached_data)

        # Fetch from API
        try:
            result = self.client.get_intraday_data(
                symbol=symbol,
                interval=interval,
            )
            data = result["data"]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = [col.split(" ")[1].lower() for col in df.columns]
            df = df.astype(float)
            df = df.sort_index()

            # Cache the data
            if use_cache:
                self.cache.set(cache_key, df.to_dict(orient="index"), ttl=300)  # 5 min TTL

            logger.info(f"Fetched intraday data for {symbol}: {len(df)} records")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch intraday data for {symbol}: {e}")
            raise

    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        use_cache: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch daily data for multiple symbols.

        Args:
            symbols: List of stock symbols.
            use_cache: Whether to use cached data.

        Returns:
            Dictionary mapping symbols to DataFrames.
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol] = self.fetch_daily_data(symbol, use_cache=use_cache)
            except Exception as e:
                logger.error(f"Failed to fetch data for {symbol}: {e}")
                continue

        return results

    def get_latest_price(self, symbol: str) -> float:
        """
        Get latest closing price for a symbol.

        Args:
            symbol: Stock symbol.

        Returns:
            Latest closing price.
        """
        df = self.fetch_daily_data(symbol, use_cache=True)
        if df.empty:
            raise ValueError(f"No data available for {symbol}")
        return float(df["close"].iloc[-1])

