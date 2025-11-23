"""
Explainability module.

Provides explanations for recommendations.
"""

from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class Explainability:
    """Provides explanations for recommendations."""

    def explain_recommendation(
        self,
        recommendation: Dict[str, Any],
        user_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate explanation for a recommendation.

        Args:
            recommendation: Recommendation dictionary.
            user_profile: User profile data.

        Returns:
            Explanation dictionary.
        """
        factors = []

        # Risk alignment
        user_risk = user_profile.get("risk_tolerance", {}).get("category", "moderate")
        rec_risk = recommendation.get("risk_level", "medium")
        if user_risk == rec_risk:
            factors.append({
                "factor": "Risk Alignment",
                "weight": 0.3,
                "impact": f"Matches your {user_risk} risk tolerance",
            })

        # Goal alignment
        user_goals = user_profile.get("financial_goals", [])
        if user_goals:
            factors.append({
                "factor": "Goal Alignment",
                "weight": 0.25,
                "impact": "Supports your financial goals",
            })

        # Diversification
        factors.append({
            "factor": "Diversification",
            "weight": 0.2,
            "impact": "Helps diversify your portfolio",
        })

        return {
            "recommendation_id": recommendation.get("instrument"),
            "reasoning": self._generate_reasoning_text(factors),
            "factors_considered": factors,
            "risk_factors": self._identify_risks(recommendation),
        }

    def _generate_reasoning_text(self, factors: List[Dict[str, Any]]) -> str:
        """Generate human-readable reasoning text."""
        reasoning_parts = []
        for factor in factors:
            reasoning_parts.append(f"{factor['factor']}: {factor['impact']}")
        return ". ".join(reasoning_parts) + "."

    def _identify_risks(self, recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify risks associated with recommendation."""
        risks = []

        risk_level = recommendation.get("risk_level", "medium")
        if risk_level == "high":
            risks.append({
                "risk": "High Volatility",
                "severity": "high",
                "mitigation": "Consider smaller allocation or dollar-cost averaging",
            })

        return risks

