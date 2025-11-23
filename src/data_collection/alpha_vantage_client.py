"""
Alpha Vantage API client with rate limiting.

Provides wrapper for Alpha Vantage API with rate limiting (5 calls/min).
"""

import time
from typing import Any, Dict, Optional

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.fundamentaldata import FundamentalData

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AlphaVantageClient:
    """Alpha Vantage API client with rate limiting."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client.

        Args:
            api_key: Alpha Vantage API key. If None, loads from config.
        """
        config = get_config()
        self.api_key = api_key or config.get("alpha_vantage.api_key")

        if not self.api_key:
            raise ValueError("Alpha Vantage API key not provided")

        # Initialize API clients
        self.ts = TimeSeries(key=self.api_key, output_format="json")
        self.ti = TechIndicators(key=self.api_key, output_format="json")
        self.sp = SectorPerformances(key=self.api_key, output_format="json")
        self.fd = FundamentalData(key=self.api_key, output_format="json")

        # Rate limiting configuration
        rate_limit_config = config.get("alpha_vantage.rate_limit", {})
        self.calls_per_minute = rate_limit_config.get("calls_per_minute", 5)
        self.min_interval = 60 / self.calls_per_minute  # seconds between calls
        self.last_call_time = 0.0
        self.call_count = 0
        self.reset_time = time.time()

    def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        current_time = time.time()

        # Reset counter every minute
        if current_time - self.reset_time >= 60:
            self.call_count = 0
            self.reset_time = current_time

        # Check if we've exceeded rate limit
        if self.call_count >= self.calls_per_minute:
            sleep_time = 60 - (current_time - self.reset_time)
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
                self.call_count = 0
                self.reset_time = time.time()

        # Ensure minimum interval between calls
        elapsed = current_time - self.last_call_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)

        self.last_call_time = time.time()
        self.call_count += 1

    def get_daily_data(
        self,
        symbol: str,
        outputsize: str = "compact",
    ) -> Dict[str, Any]:
        """
        Get daily stock data.

        Args:
            symbol: Stock symbol (e.g., 'AAPL').
            outputsize: 'compact' (last 100 data points) or 'full' (full history).

        Returns:
            Dictionary containing time series data and metadata.
        """
        self._rate_limit()
        try:
            data, meta = self.ts.get_daily(symbol=symbol, outputsize=outputsize)
            logger.debug(f"Fetched daily data for {symbol}")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching daily data for {symbol}: {e}")
            raise

    def get_intraday_data(
        self,
        symbol: str,
        interval: str = "5min",
        outputsize: str = "compact",
    ) -> Dict[str, Any]:
        """
        Get intraday stock data.

        Args:
            symbol: Stock symbol.
            interval: Time interval ('1min', '5min', '15min', '30min', '60min').
            outputsize: 'compact' or 'full'.

        Returns:
            Dictionary containing intraday data and metadata.
        """
        self._rate_limit()
        try:
            data, meta = self.ts.get_intraday(
                symbol=symbol,
                interval=interval,
                outputsize=outputsize,
            )
            logger.debug(f"Fetched intraday data for {symbol}")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching intraday data for {symbol}: {e}")
            raise

    def get_rsi(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 14,
        series_type: str = "close",
    ) -> Dict[str, Any]:
        """
        Get Relative Strength Index (RSI) indicator.

        Args:
            symbol: Stock symbol.
            interval: Time interval.
            time_period: Number of data points for RSI calculation.
            series_type: 'close', 'open', 'high', 'low'.

        Returns:
            Dictionary containing RSI data and metadata.
        """
        self._rate_limit()
        try:
            data, meta = self.ti.get_rsi(
                symbol=symbol,
                interval=interval,
                time_period=time_period,
                series_type=series_type,
            )
            logger.debug(f"Fetched RSI for {symbol}")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching RSI for {symbol}: {e}")
            raise

    def get_macd(
        self,
        symbol: str,
        interval: str = "daily",
        series_type: str = "close",
    ) -> Dict[str, Any]:
        """
        Get MACD (Moving Average Convergence Divergence) indicator.

        Args:
            symbol: Stock symbol.
            interval: Time interval.
            series_type: 'close', 'open', 'high', 'low'.

        Returns:
            Dictionary containing MACD data and metadata.
        """
        self._rate_limit()
        try:
            data, meta = self.ti.get_macd(
                symbol=symbol,
                interval=interval,
                series_type=series_type,
            )
            logger.debug(f"Fetched MACD for {symbol}")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching MACD for {symbol}: {e}")
            raise

    def get_bollinger_bands(
        self,
        symbol: str,
        interval: str = "daily",
        time_period: int = 20,
        series_type: str = "close",
    ) -> Dict[str, Any]:
        """
        Get Bollinger Bands indicator.

        Args:
            symbol: Stock symbol.
            interval: Time interval.
            time_period: Number of periods.
            series_type: 'close', 'open', 'high', 'low'.

        Returns:
            Dictionary containing Bollinger Bands data and metadata.
        """
        self._rate_limit()
        try:
            data, meta = self.ti.get_bbands(
                symbol=symbol,
                interval=interval,
                time_period=time_period,
                series_type=series_type,
            )
            logger.debug(f"Fetched Bollinger Bands for {symbol}")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching Bollinger Bands for {symbol}: {e}")
            raise

    def get_sector_performance(self) -> Dict[str, Any]:
        """
        Get sector performance data.

        Returns:
            Dictionary containing sector performance data.
        """
        self._rate_limit()
        try:
            data, meta = self.sp.get_sector()
            logger.debug("Fetched sector performance data")
            return {"data": data, "metadata": meta}
        except Exception as e:
            logger.error(f"Error fetching sector performance: {e}")
            raise

