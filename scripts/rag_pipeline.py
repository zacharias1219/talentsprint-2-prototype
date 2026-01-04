"""
RAG Pipeline: Integrating Market Data + User Context for the LLM.

This script demonstrates the Retrieval-Augmented Generation (RAG) flow:
1. Context Construction: Combines user profile, recommendation, and live market data.
2. Prompt Engineering: Feeds this context into a prompt template.
3. Response Generation: Simulates the LLM's answer (since we don't have a live inference server running yet).
"""

import os
import json
from datetime import datetime
from typing import Dict, Any

import sys
# Add current directory to path so we can import from siblings
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our existing modules
# (In a real app, these would be imported from src packages)
try:
    from personalization_engine import PersonalizationEngine
    PERSONALIZATION_AVAILABLE = True
except ImportError:
    print("Warning: Could not import PersonalizationEngine. Using fallback.")
    PERSONALIZATION_AVAILABLE = False
    # Fallback class
    class PersonalizationEngine:
        def load_profiles(self, filepath):
            return []

# We'll use a simplified mock for the Alpha Vantage client to avoid re-fetching 
# if the API limit is hit, but the structure mimics the real one.
class MockMarketData:
    def get_context(self, tickers=["AAPL", "MSFT", "GOOGL"]):
        return {
            "AAPL": {"price": 185.60, "trend": "Bullish", "rsi": 58.4},
            "MSFT": {"price": 370.25, "trend": "Neutral", "rsi": 51.2},
            "GOOGL": {"price": 140.10, "trend": "Bullish", "rsi": 62.1},
            "VTI": {"price": 225.40, "trend": "Bullish", "desc": "Total Stock Market ETF"},
            "BND": {"price": 72.30, "trend": "Bearish", "desc": "Total Bond Market ETF"}
        }

class FinancialRAGPipeline:
    def __init__(self):
        if PERSONALIZATION_AVAILABLE:
            self.personalization = PersonalizationEngine()
        else:
            self.personalization = None
        self.market_data = MockMarketData()
        
    def retrieve_context(self, user_id: str, query: str) -> str:
        """
        Builds the context window for the LLM.
        Combines: User Recommendation + Relevant Market Data
        """
        # 1. Get User Data
        # In a real app, fetch from DB. Here, load from JSON.
        try:
            with open("data/processed/user_recommendations.json", "r") as f:
                all_recs = json.load(f)
        except FileNotFoundError:
            return "Error: user_recommendations.json not found. Please run personalization_engine.py first."
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in user_recommendations.json: {e}"
            
        user_rec = next((r for r in all_recs if r["user_id"] == user_id), None)
        if not user_rec:
            return "User not found."

        # 2. Get Market Data (Naive retrieval: get everything for now)
        # In production, you'd use vector search to find ONLY relevant stocks
        market_snapshot = self.market_data.get_context()
        
        # 3. Construct Context String
        context = f"""
--- USER CONTEXT ---
User ID: {user_id}
Risk Profile: {user_rec['risk_profile']['label']} (Score: {user_rec['risk_profile']['score']})
Target Allocation: {user_rec['target_allocation']}
Recommended Sectors: {', '.join(user_rec['suggested_sectors'])}
Action Plan: {'; '.join(user_rec['action_plan'])}

--- MARKET CONTEXT (Live) ---
Today's Date: {datetime.now().strftime('%Y-%m-%d')}
Market Snapshot:
{json.dumps(market_snapshot, indent=2)}
"""
        return context

    def generate_response(self, user_id: str, query: str) -> str:
        """
        Simulates the LLM generation step.
        """
        context = self.retrieve_context(user_id, query)
        
        # Prompt Template
        prompt = f"""
SYSTEM: You are an expert Financial Advisor AI. Use the provided context to answer the user's question. 
Be specific, citing the user's risk profile and current market data.

CONTEXT:
{context}

USER QUESTION:
"{query}"

### MOCK LLM RESPONSE (Generated based on logic):
"""
        # Since we don't have a running LLM inference server here, 
        # we will deterministically generate a response that LOOKS like what the LLM would say.
        
        try:
            risk_profile_part = context.split('Risk Profile: ')
            if len(risk_profile_part) > 1:
                 risk_profile = risk_profile_part[1].split(' (')[0]
            else:
                 risk_profile = "Unknown"
            
            response = f"Based on your **{risk_profile}** risk profile, "
        except IndexError:
             response = "Based on your risk profile, "
        
        if "mutual funds" in query.lower() or "etfs" in query.lower():
            response += "I recommend focusing on broad market ETFs like **VTI** (Total Stock Market) which is currently showing a **Bullish** trend "
            response += "around $225.40. "
            response += f"Given your goal to increase stock allocation, this aligns with your target."
        elif "apple" in query.lower() or "aapl" in query.lower():
            response += "Apple (AAPL) is trading at $185.60 with a **Bullish** trend (RSI 58.4). "
            response += "While it fits your growth goals, ensure it doesn't exceed 5% of your portfolio to maintain diversification."
        else:
            try:
                action_plan_part = context.split("Action Plan: ")
                if len(action_plan_part) > 1:
                    action = action_plan_part[1].split("\n")[0]
                    response += "I recommend following your action plan: " + action
                else:
                    response += "I recommend reviewing your action plan."
            except IndexError:
                response += "I recommend reviewing your action plan."

        return prompt + response

def main():
    rag = FinancialRAGPipeline()
    
    # Test Case 1: ETF Question
    user_id = "user_1000" # The "Moderately Aggressive" user from before
    query = "Should I invest in mutual funds or ETFs this year?"
    
    print(f"\n{'='*20} RAG PIPELINE TEST 1 {'='*20}")
    print(f"Query: {query}")
    output = rag.generate_response(user_id, query)
    print(output)

    # Test Case 2: Stock Specific Question
    query_2 = "What do you think about buying Apple right now?"
    print(f"\n{'='*20} RAG PIPELINE TEST 2 {'='*20}")
    print(f"Query: {query_2}")
    output_2 = rag.generate_response(user_id, query_2)
    print(output_2)

if __name__ == "__main__":
    main()

