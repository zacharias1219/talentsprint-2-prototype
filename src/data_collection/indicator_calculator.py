"""
Technical indicator calculator module.

Calculates technical indicators like RSI, MACD, Bollinger Bands.
"""

from typing import Dict, Optional

import pandas as pd

from src.data_collection.alpha_vantage_client import AlphaVantageClient
from src.data_collection.cache_manager import CacheManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class IndicatorCalculator:
    """Calculator for technical indicators."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        """
        Initialize indicator calculator.

        Args:
            cache_manager: Optional cache manager instance.
        """
        self.client = AlphaVantageClient()
        self.cache = cache_manager or CacheManager()

    def calculate_rsi(
        self,
        symbol: str,
        period: int = 14,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Calculate RSI (Relative Strength Index).

        Args:
            symbol: Stock symbol.
            period: Number of periods for RSI calculation.
            use_cache: Whether to use cached data.

        Returns:
            DataFrame with RSI values.
        """
        cache_key = f"rsi_{symbol}_{period}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached RSI for {symbol}")
                return pd.DataFrame(cached_data)

        try:
            result = self.client.get_rsi(
                symbol=symbol,
                interval="daily",
                time_period=period,
            )
            data = result["data"]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = ["RSI"]
            df["RSI"] = pd.to_numeric(df["RSI"], errors="coerce")
            df = df.sort_index()

            if use_cache:
                self.cache.set(cache_key, df.to_dict(orient="index"))

            logger.debug(f"Calculated RSI for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to calculate RSI for {symbol}: {e}")
            raise

    def calculate_macd(
        self,
        symbol: str,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            symbol: Stock symbol.
            use_cache: Whether to use cached data.

        Returns:
            DataFrame with MACD, Signal, and Histogram values.
        """
        cache_key = f"macd_{symbol}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached MACD for {symbol}")
                return pd.DataFrame(cached_data)

        try:
            result = self.client.get_macd(symbol=symbol, interval="daily")
            data = result["data"]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = ["MACD", "MACD_Signal", "MACD_Hist"]
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.sort_index()

            if use_cache:
                self.cache.set(cache_key, df.to_dict(orient="index"))

            logger.debug(f"Calculated MACD for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to calculate MACD for {symbol}: {e}")
            raise

    def calculate_bollinger_bands(
        self,
        symbol: str,
        period: int = 20,
        use_cache: bool = True,
    ) -> pd.DataFrame:
        """
        Calculate Bollinger Bands.

        Args:
            symbol: Stock symbol.
            period: Number of periods.
            use_cache: Whether to use cached data.

        Returns:
            DataFrame with Upper, Middle, and Lower Bollinger Bands.
        """
        cache_key = f"bbands_{symbol}_{period}"

        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Using cached Bollinger Bands for {symbol}")
                return pd.DataFrame(cached_data)

        try:
            result = self.client.get_bollinger_bands(
                symbol=symbol,
                interval="daily",
                time_period=period,
            )
            data = result["data"]

            # Convert to DataFrame
            df = pd.DataFrame.from_dict(data, orient="index")
            df.index = pd.to_datetime(df.index)
            df.columns = ["BB_Upper", "BB_Middle", "BB_Lower"]
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            df = df.sort_index()

            if use_cache:
                self.cache.set(cache_key, df.to_dict(orient="index"))

            logger.debug(f"Calculated Bollinger Bands for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to calculate Bollinger Bands for {symbol}: {e}")
            raise

    def get_all_indicators(
        self,
        symbol: str,
        use_cache: bool = True,
    ) -> Dict[str, pd.DataFrame]:
        """
        Get all technical indicators for a symbol.

        Args:
            symbol: Stock symbol.
            use_cache: Whether to use cached data.

        Returns:
            Dictionary mapping indicator names to DataFrames.
        """
        indicators = {}

        try:
            indicators["RSI"] = self.calculate_rsi(symbol, use_cache=use_cache)
        except Exception as e:
            logger.warning(f"Failed to calculate RSI: {e}")

        try:
            indicators["MACD"] = self.calculate_macd(symbol, use_cache=use_cache)
        except Exception as e:
            logger.warning(f"Failed to calculate MACD: {e}")

        try:
            indicators["Bollinger_Bands"] = self.calculate_bollinger_bands(
                symbol,
                use_cache=use_cache,
            )
        except Exception as e:
            logger.warning(f"Failed to calculate Bollinger Bands: {e}")

        return indicators

