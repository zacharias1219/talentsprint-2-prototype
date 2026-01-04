"""
Data Acquisition Script for Financial Advisor Project.

This script demonstrates how to acquire data from the three main sources identified:
1. Market Data (Alpha Vantage)
2. Financial News & Sentiment (Alpha Vantage + External)
3. LLM Fine-tuning Data (Hugging Face - FinGPT)
4. User Profile Data (Synthetic Generation)
"""

import os
import json
import random
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
from dotenv import load_dotenv

# Try to import datasets, handle if not installed
try:
    from datasets import load_dataset
except ImportError:
    print("Hugging Face 'datasets' library not found. Install with: pip install datasets")
    load_dataset = None

# Import local client if available, else mock
try:
    from src.data_collection.alpha_vantage_client import AlphaVantageClient
except ImportError:
    # Mock for standalone usage
    class AlphaVantageClient:
        def __init__(self, api_key): self.api_key = api_key
        def get_daily_data(self, symbol, outputsize="compact"):
            # Return a dict structure compatible with what the code expects in fallback
            # Structure: { "data": { "YYYY-MM-DD": { "4. close": "150.00" } } }
            return {"data": {"2023-01-01": {"4. close": "150.00"}}, "metadata": {}}

def get_alpha_vantage_news(api_key: str, tickers: str = "AAPL") -> Dict:
    """
    Fetch News & Sentiment data from Alpha Vantage.
    This endpoint provides live news and sentiment scores.
    """
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={tickers}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching news: {e}")
        return {}

def load_fingpt_datasets():
    """
    Load key datasets for fine-tuning the Financial LLM.
    Focuses on FinGPT related datasets available on Hugging Face.
    """
    print("\n--- Loading Financial Fine-tuning Datasets ---")
    
    if load_dataset is None:
        print("Skipping Hugging Face dataset loading: 'datasets' library not found.")
        return {}

    datasets_to_load = [
        {
            "name": "FinGPT/fingpt-sentiment-train",
            "description": "Financial Sentiment Analysis Training Data",
            "split": "train" 
        },
        {
            "name": "FinGPT/fingpt-fiqa_qa",
            "description": "Financial QA Dataset for Advisory Logic",
            "split": "train"
        }
    ]

    loaded_data = {}
    
    for ds_info in datasets_to_load:
        try:
            print(f"Loading {ds_info['name']}...")
            # Streaming=True allows loading without downloading the whole dataset immediately
            dataset = load_dataset(ds_info['name'], split=ds_info['split'], streaming=True)
            
            # Get first 2 examples to show structure
            examples = list(dataset.take(2))
            loaded_data[ds_info['name']] = examples
            
            print(f"Successfully loaded sample from {ds_info['name']}")
            print(f"Sample entry: {json.dumps(examples[0], indent=2)}")
            
        except Exception as e:
            print(f"Failed to load {ds_info['name']}: {e}")
            
    return loaded_data

def generate_synthetic_user_profiles(count: int = 5) -> List[Dict]:
    """
    Generate synthetic user profiles for testing the Personalization Engine.
    """
    print(f"\n--- Generating {count} Synthetic User Profiles ---")
    
    risk_tolerances = ["Low", "Moderate", "High", "Very High"]
    goals = ["Retirement", "Home Purchase", "Wealth Generation", "Education", "Emergency Fund"]
    
    profiles = []
    for i in range(count):
        profile = {
            "user_id": f"user_{1000+i}",
            "age": random.randint(22, 65),
            "income": random.randint(40000, 250000),
            "savings": random.randint(5000, 500000),
            "risk_tolerance": random.choice(risk_tolerances),
            "investment_horizon_years": random.randint(1, 40),
            "financial_goals": random.sample(goals, k=random.randint(1, 2)),
            "current_portfolio": {
                "stocks": random.randint(0, 80),
                "bonds": random.randint(0, 60),
                "cash": random.randint(5, 40)
            }
        }
        profiles.append(profile)
    
    print(json.dumps(profiles[0], indent=2))
    return profiles

def main():
    # Configuration
    # Load API key from environment variable or .env file
    load_dotenv()
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    
    print("=== 1. Market Data (Alpha Vantage) ===")
    # Using real client logic now that we have a key
    client = AlphaVantageClient(api_key=API_KEY)
    try:
        # Get Daily Data for Apple (Real API Call)
        print("Fetching daily data for AAPL...")
        # Use 'compact' to save API calls and bandwidth for testing
        daily_data = client.get_daily_data("AAPL", outputsize="compact")
        
        # Print first date to verify
        if daily_data and "data" in daily_data and isinstance(daily_data["data"], dict):
             dates = list(daily_data["data"].keys())
             if dates:
                 latest_date = dates[0]
                 latest_close = daily_data["data"][latest_date].get("4. close", "N/A")
                 print(f"Success! AAPL Close ({latest_date}): ${latest_close}")
             else:
                 print("Data format empty.")
        else:
             print("Data format unexpected or empty.")

             
    except Exception as e:
        print(f"Market data fetch failed: {e}")

    print("\n=== 2. News & Sentiment Data ===")
    if API_KEY and API_KEY != "YOUR_API_KEY_HERE":
        print("Fetching news for MSFT...")
        news_data = get_alpha_vantage_news(API_KEY, "MSFT")
        feed = news_data.get('feed', [])
        print(f"Fetched {len(feed)} news items.")
        if feed:
            print(f"Headline: {feed[0].get('title')}")
            print(f"Sentiment Score: {feed[0].get('overall_sentiment_score')}")
    else:
        print("Skipping actual API call (no key provided).")
        print("Use 'get_alpha_vantage_news' function for Sentiment Data.")

    print("\n=== 3. LLM Fine-Tuning Data (FinGPT) ===")
    # This requires 'datasets' library
    fingpt_data = load_fingpt_datasets()

    print("\n=== 4. User Profile Data (Personalization) ===")
    profiles = generate_synthetic_user_profiles()
    
    # Save generated profiles for use
    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/synthetic_profiles.json", "w") as f:
        json.dump(profiles, f, indent=2)
    print("Saved synthetic profiles to data/processed/synthetic_profiles.json")

if __name__ == "__main__":
    main()

