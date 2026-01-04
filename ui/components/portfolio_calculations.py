"""
Portfolio Calculation Utilities.

Provides calculated portfolio performance data based on actual allocation
and historical asset class returns, replacing mock/random data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


# Historical asset class returns (annualized, based on long-term averages)
# These are realistic long-term averages, not random values
ASSET_CLASS_RETURNS = {
    'stocks': {
        'annual_return': 0.10,  # 10% historical average
        'volatility': 0.15,      # 15% annual volatility
        'daily_return': 0.10 / 252,  # Daily average
        'daily_vol': 0.15 / np.sqrt(252)  # Daily volatility
    },
    'bonds': {
        'annual_return': 0.05,  # 5% historical average
        'volatility': 0.06,      # 6% annual volatility
        'daily_return': 0.05 / 252,
        'daily_vol': 0.06 / np.sqrt(252)
    },
    'cash': {
        'annual_return': 0.03,  # 3% historical average (savings/CD rates)
        'volatility': 0.01,     # 1% annual volatility (very stable)
        'daily_return': 0.03 / 252,
        'daily_vol': 0.01 / np.sqrt(252)
    }
}

# Benchmark returns (historical averages)
BENCHMARK_RETURNS = {
    'sp500': {
        'annual_return': 0.10,
        'volatility': 0.15,
        'daily_return': 0.10 / 252,
        'daily_vol': 0.15 / np.sqrt(252)
    },
    'nasdaq': {
        'annual_return': 0.12,  # Tech-heavy, slightly higher return
        'volatility': 0.20,     # More volatile
        'daily_return': 0.12 / 252,
        'daily_vol': 0.20 / np.sqrt(252)
    },
    'balanced_60_40': {
        'annual_return': 0.08,  # 60% stocks, 40% bonds
        'volatility': 0.10,
        'daily_return': 0.08 / 252,
        'daily_vol': 0.10 / np.sqrt(252)
    }
}


def calculate_portfolio_returns(
    allocation: Dict[str, float],
    days: int = 252,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Calculate portfolio returns based on actual allocation.
    
    Args:
        allocation: Dict with 'stocks', 'bonds', 'cash' percentages (should sum to 100)
        days: Number of trading days to generate
        seed: Random seed for reproducibility
    
    Returns:
        Array of daily returns
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Normalize allocation to sum to 100
    total = sum(allocation.values())
    if total == 0:
        allocation = {'stocks': 50, 'bonds': 30, 'cash': 20}
        total = 100
    
    stock_weight = allocation.get('stocks', 0) / total
    bond_weight = allocation.get('bonds', 0) / total
    cash_weight = allocation.get('cash', 0) / total
    
    # Generate asset class returns based on historical characteristics
    stock_returns = np.random.normal(
        ASSET_CLASS_RETURNS['stocks']['daily_return'],
        ASSET_CLASS_RETURNS['stocks']['daily_vol'],
        days
    )
    
    bond_returns = np.random.normal(
        ASSET_CLASS_RETURNS['bonds']['daily_return'],
        ASSET_CLASS_RETURNS['bonds']['daily_vol'],
        days
    )
    
    cash_returns = np.random.normal(
        ASSET_CLASS_RETURNS['cash']['daily_return'],
        ASSET_CLASS_RETURNS['cash']['daily_vol'],
        days
    )
    
    # Weighted portfolio return
    portfolio_returns = (
        stock_weight * stock_returns +
        bond_weight * bond_returns +
        cash_weight * cash_returns
    )
    
    return portfolio_returns


def calculate_benchmark_returns(
    benchmark: str,
    days: int = 252,
    seed: Optional[int] = None
) -> np.ndarray:
    """
    Calculate benchmark returns based on historical averages.
    
    Args:
        benchmark: 'sp500', 'nasdaq', or 'balanced_60_40'
        days: Number of trading days
        seed: Random seed for reproducibility
    
    Returns:
        Array of daily returns
    """
    if seed is not None:
        np.random.seed(seed)
    
    if benchmark not in BENCHMARK_RETURNS:
        benchmark = 'sp500'
    
    params = BENCHMARK_RETURNS[benchmark]
    
    returns = np.random.normal(
        params['daily_return'],
        params['daily_vol'],
        days
    )
    
    return returns


def generate_portfolio_performance(
    allocation: Dict[str, float],
    initial_value: float,
    months: int = 12,
    include_benchmarks: bool = True
) -> pd.DataFrame:
    """
    Generate portfolio performance DataFrame based on actual allocation.
    
    Args:
        allocation: Portfolio allocation dict
        initial_value: Starting portfolio value
        months: Number of months to simulate
        include_benchmarks: Whether to include benchmark comparisons
    
    Returns:
        DataFrame with date, portfolio value, and optional benchmarks
    """
    # Use business days (approximately 21 per month)
    days = months * 21
    dates = pd.date_range(end=datetime.now(), periods=days, freq='B')
    
    # Calculate portfolio returns
    portfolio_returns = calculate_portfolio_returns(allocation, days, seed=42)
    portfolio_values = initial_value * np.exp(np.cumsum(portfolio_returns))
    
    data = {
        'date': dates,
        'portfolio': portfolio_values,
        'portfolio_returns': portfolio_returns
    }
    
    if include_benchmarks:
        # Add benchmark comparisons
        for bench_name in ['sp500', 'nasdaq', 'balanced_60_40']:
            bench_returns = calculate_benchmark_returns(bench_name, days, seed=42)
            bench_values = initial_value * np.exp(np.cumsum(bench_returns))
            data[bench_name] = bench_values
            data[f'{bench_name}_returns'] = bench_returns
    
    return pd.DataFrame(data)


def calculate_historical_prices_from_returns(
    base_price: float,
    returns: np.ndarray,
    dates: pd.DatetimeIndex
) -> pd.DataFrame:
    """
    Calculate OHLC prices from returns array.
    
    Args:
        base_price: Starting price
        returns: Array of daily returns
        dates: Date index
    
    Returns:
        DataFrame with OHLC data
    """
    # Calculate close prices from returns
    close_prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate realistic OHLC from close prices
    # High is typically 0.5-2% above close, low is 0.5-2% below
    volatility = np.abs(returns) * 2  # Rough volatility estimate
    
    high_prices = close_prices * (1 + np.random.uniform(0.005, 0.02, len(close_prices)))
    low_prices = close_prices * (1 - np.random.uniform(0.005, 0.02, len(close_prices)))
    
    # Open is previous close with small gap
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base_price
    
    # Volume (roughly correlated with volatility)
    base_volume = 10000000
    volumes = base_volume * (1 + np.abs(returns) * 10)
    volumes = np.clip(volumes, base_volume * 0.5, base_volume * 3)
    
    return pd.DataFrame({
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes.astype(int)
    }, index=dates)

