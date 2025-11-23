"""
Data validation module.

Validates and cleans financial data from APIs.
"""

from typing import Any, Dict, List, Optional

import pandas as pd

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DataValidator:
    """Validator for financial data."""

    @staticmethod
    def validate_stock_data(df: pd.DataFrame) -> bool:
        """
        Validate stock data DataFrame.

        Args:
            df: DataFrame with stock data.

        Returns:
            True if valid, False otherwise.
        """
        if df.empty:
            logger.warning("Stock data DataFrame is empty")
            return False

        # Check required columns
        required_columns = ["open", "high", "low", "close", "volume"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing required columns: {missing_columns}")
            return False

        # Check for negative values
        numeric_columns = ["open", "high", "low", "close", "volume"]
        for col in numeric_columns:
            if col in df.columns:
                if (df[col] < 0).any():
                    logger.warning(f"Negative values found in {col}")
                    return False

        # Check high >= low
        if "high" in df.columns and "low" in df.columns:
            if (df["high"] < df["low"]).any():
                logger.warning("High values less than low values found")
                return False

        # Check high >= close and low <= close
        if all(col in df.columns for col in ["high", "low", "close"]):
            if (df["high"] < df["close"]).any() or (df["low"] > df["close"]).any():
                logger.warning("Price inconsistencies found")
                return False

        return True

    @staticmethod
    def clean_stock_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean stock data DataFrame.

        Args:
            df: DataFrame with stock data.

        Returns:
            Cleaned DataFrame.
        """
        df_clean = df.copy()

        # Remove duplicates
        df_clean = df_clean.drop_duplicates()

        # Sort by index (date)
        df_clean = df_clean.sort_index()

        # Remove rows with missing critical data
        required_columns = ["open", "high", "low", "close"]
        df_clean = df_clean.dropna(subset=required_columns)

        # Fill missing volume with 0
        if "volume" in df_clean.columns:
            df_clean["volume"] = df_clean["volume"].fillna(0)

        # Ensure high >= low
        if "high" in df_clean.columns and "low" in df_clean.columns:
            df_clean["high"] = df_clean[["high", "low"]].max(axis=1)
            df_clean["low"] = df_clean[["high", "low"]].min(axis=1)

        # Ensure high >= close >= low
        if all(col in df_clean.columns for col in ["high", "low", "close"]):
            df_clean["close"] = df_clean["close"].clip(
                lower=df_clean["low"],
                upper=df_clean["high"],
            )

        logger.debug(f"Cleaned stock data: {len(df)} -> {len(df_clean)} rows")
        return df_clean

    @staticmethod
    def validate_indicator_data(df: pd.DataFrame, indicator_name: str) -> bool:
        """
        Validate technical indicator data.

        Args:
            df: DataFrame with indicator data.
            indicator_name: Name of the indicator.

        Returns:
            True if valid, False otherwise.
        """
        if df.empty:
            logger.warning(f"{indicator_name} DataFrame is empty")
            return False

        # Check for infinite values
        if df.isin([float("inf"), float("-inf")]).any().any():
            logger.warning(f"Infinite values found in {indicator_name}")
            return False

        # RSI should be between 0 and 100
        if indicator_name == "RSI":
            if "RSI" in df.columns:
                if (df["RSI"] < 0).any() or (df["RSI"] > 100).any():
                    logger.warning("RSI values outside valid range [0, 100]")
                    return False

        return True

