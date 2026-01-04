"""
Personalization Engine: Profile Matching & Recommendation Logic.

This script takes user profiles (generated previously) and:
1. Maps them to investment personas using rule-based logic + scoring.
2. Recommends asset allocation (Stocks/Bonds/Cash).
3. Suggests specific sectors based on risk tolerance.
"""

import json
import os
import pandas as pd
from typing import Dict, List, Any

class PersonalizationEngine:
    def __init__(self):
        # Standard Investment Portfolios based on Risk Tolerance
        self.model_portfolios = {
            "Conservative": {"stocks": 20, "bonds": 70, "cash": 10},
            "Moderately Conservative": {"stocks": 40, "bonds": 50, "cash": 10},
            "Moderate": {"stocks": 60, "bonds": 35, "cash": 5},
            "Moderately Aggressive": {"stocks": 80, "bonds": 15, "cash": 5},
            "Aggressive": {"stocks": 90, "bonds": 10, "cash": 0},
            "Very Aggressive": {"stocks": 100, "bonds": 0, "cash": 0}
        }
        
        # Sector recommendations based on goals/horizon
        self.sector_map = {
            "Wealth Generation": ["Technology", "Consumer Discretionary", "Financials"],
            "Retirement": ["Healthcare", "Consumer Staples", "Utilities", "Dividend Aristocrats"],
            "Home Purchase": ["Real Estate (REITs)", "Bonds", "High Yield Savings"],
            "Emergency Fund": ["Money Market", "Treasury Bills"],
            "Education": ["Index Funds", "Technology"]
        }

    def load_profiles(self, filepath: str) -> List[Dict]:
        """Load user profiles from JSON file."""
        if not os.path.exists(filepath):
            print(f"Error: File {filepath} not found. Run data_acquisition.py first.")
            return []
        with open(filepath, 'r') as f:
            return json.load(f)

    def _calculate_risk_score(self, profile: Dict) -> int:
        """
        Calculate a numeric risk score (0-100) based on profile attributes.
        """
        score = 50 # Base score
        
        # Age factor: Younger = higher risk capacity
        age = profile.get("age", 30)
        if age < 35: score += 20
        elif age < 50: score += 10
        elif age > 65: score -= 20
        
        # Income/Savings factor (Wealth capacity)
        income = profile.get("income", 0)
        savings = profile.get("savings", 0)
        wealth_ratio = savings / (income + 1) # Avoid div/0
        if wealth_ratio > 2.0: score += 15
        elif wealth_ratio < 0.5: score -= 10
        
        # Stated Risk Tolerance (Psychological)
        tolerance = profile.get("risk_tolerance", "Moderate")
        tolerance_map = {
            "Low": -25, "Moderate": 0, "High": 20, "Very High": 30
        }
        score += tolerance_map.get(tolerance, 0)
        
        # Horizon
        horizon = profile.get("investment_horizon_years", 10)
        if horizon > 20: score += 15
        elif horizon < 5: score -= 20
        
        # Clamp score
        return max(0, min(100, score))

    def _map_score_to_portfolio(self, score: int) -> str:
        """Map numeric score to portfolio label."""
        if score < 20: return "Conservative"
        if score < 40: return "Moderately Conservative"
        if score < 60: return "Moderate"
        if score < 80: return "Moderately Aggressive"
        if score < 90: return "Aggressive"
        return "Very Aggressive"

    def generate_recommendation(self, profile: Dict) -> Dict:
        """
        Generate a full financial recommendation for a single user.
        """
        risk_score = self._calculate_risk_score(profile)
        portfolio_type = self._map_score_to_portfolio(risk_score)
        target_allocation = self.model_portfolios[portfolio_type]
        
        # Determine gaps
        current = profile.get("current_portfolio", {"stocks":0, "bonds":0, "cash":100})
        gaps = {
            "stocks": target_allocation["stocks"] - current.get("stocks", 0),
            "bonds": target_allocation["bonds"] - current.get("bonds", 0),
            "cash": target_allocation["cash"] - current.get("cash", 0)
        }
        
        # Sector picks
        goals = profile.get("financial_goals", [])
        suggested_sectors = set()
        for goal in goals:
            picks = self.sector_map.get(goal, [])
            suggested_sectors.update(picks)
            
        return {
            "user_id": profile["user_id"],
            "risk_profile": {
                "score": risk_score,
                "label": portfolio_type
            },
            "target_allocation": target_allocation,
            "allocation_gaps": gaps,
            "suggested_sectors": list(suggested_sectors),
            "action_plan": self._generate_action_plan(gaps, list(suggested_sectors))
        }

    def _generate_action_plan(self, gaps: Dict, sectors: List[str]) -> List[str]:
        """Generate plain-text action items."""
        actions = []
        
        # Rebalancing actions
        if gaps["stocks"] > 5:
            actions.append(f"Increase Stock allocation by {gaps['stocks']}% to boost growth.")
        elif gaps["stocks"] < -5:
            actions.append(f"Reduce Stock exposure by {abs(gaps['stocks'])}% to lock in gains/reduce risk.")
            
        if gaps["cash"] < -5:
            actions.append(f"You are holding too much cash. Deploy {abs(gaps['cash'])}% into markets.")
        elif gaps["cash"] > 5:
            actions.append(f"Build up Cash reserves by {gaps['cash']}% for stability/liquidity.")
            
        # Sector actions
        if sectors:
            sector_str = ", ".join(sectors[:3])
            actions.append(f"Consider overweighting these sectors based on your goals: {sector_str}.")
            
        return actions

def main():
    engine = PersonalizationEngine()
    
    # Load profiles generated by data_acquisition.py
    input_path = "data/processed/synthetic_profiles.json"
    profiles = engine.load_profiles(input_path)
    
    if not profiles:
        return

    print(f"--- Processing {len(profiles)} User Profiles ---\n")
    
    recommendations = []
    for p in profiles:
        rec = engine.generate_recommendation(p)
        recommendations.append(rec)
        
        # Print Summary for first 2 users
        if len(recommendations) <= 2:
            print(f"User: {rec['user_id']} | Goal: {p['financial_goals']}")
            print(f"Risk Score: {rec['risk_profile']['score']} ({rec['risk_profile']['label']})")
            print(f"Target Allocation: {rec['target_allocation']}")
            print(f"Action Plan: {rec['action_plan']}")
            print("-" * 60)
            
    # Save recommendations
    output_path = "data/processed/user_recommendations.json"
    with open(output_path, 'w') as f:
        json.dump(recommendations, f, indent=2)
    print(f"\nSaved all recommendations to {output_path}")

if __name__ == "__main__":
    main()







