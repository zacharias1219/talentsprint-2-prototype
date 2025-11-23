"""
Risk assessor module.

Calculates risk tolerance scores and categories.
"""

from datetime import datetime
from typing import Any, Dict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RiskAssessor:
    """Assesses user risk tolerance."""

    def calculate_risk_score(
        self,
        age: int,
        income: float,
        investment_experience: str,
        time_horizon: str,
        loss_tolerance: str,
    ) -> float:
        """
        Calculate risk tolerance score (0.0 to 1.0).

        Args:
            age: User age.
            income: Annual income.
            investment_experience: 'beginner', 'intermediate', 'advanced'.
            time_horizon: 'short', 'medium', 'long'.
            loss_tolerance: 'low', 'medium', 'high'.

        Returns:
            Risk score between 0.0 and 1.0.
        """
        score = 0.5  # Base score

        # Age factor (younger = higher risk tolerance)
        if age < 30:
            score += 0.2
        elif age < 50:
            score += 0.1
        elif age >= 65:
            score -= 0.2

        # Income factor (higher income = higher risk tolerance)
        if income >= 200000:
            score += 0.15
        elif income >= 100000:
            score += 0.1
        elif income < 50000:
            score -= 0.1

        # Investment experience
        experience_map = {
            "beginner": -0.15,
            "intermediate": 0.0,
            "advanced": 0.15,
        }
        score += experience_map.get(investment_experience.lower(), 0.0)

        # Time horizon
        horizon_map = {
            "short": -0.2,
            "medium": 0.0,
            "long": 0.2,
        }
        score += horizon_map.get(time_horizon.lower(), 0.0)

        # Loss tolerance
        loss_map = {
            "low": -0.2,
            "medium": 0.0,
            "high": 0.2,
        }
        score += loss_map.get(loss_tolerance.lower(), 0.0)

        # Clamp between 0 and 1
        score = max(0.0, min(1.0, score))

        return score

    def get_risk_category(self, risk_score: float) -> str:
        """
        Get risk category from score.

        Args:
            risk_score: Risk score (0.0 to 1.0).

        Returns:
            Risk category ('conservative', 'moderate', 'aggressive').
        """
        if risk_score < 0.33:
            return "conservative"
        elif risk_score < 0.67:
            return "moderate"
        else:
            return "aggressive"

    def assess_risk(
        self,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Assess risk tolerance from profile data.

        Args:
            profile_data: User profile data.

        Returns:
            Dictionary with risk assessment results.
        """
        demographics = profile_data.get("demographics", {})
        risk_factors = profile_data.get("risk_tolerance", {}).get("factors", {})

        risk_score = self.calculate_risk_score(
            age=demographics.get("age", 35),
            income=demographics.get("income", 50000),
            investment_experience=risk_factors.get("investment_experience", "beginner"),
            time_horizon=risk_factors.get("time_horizon", "medium"),
            loss_tolerance=risk_factors.get("loss_tolerance", "medium"),
        )

        risk_category = self.get_risk_category(risk_score)

        return {
            "score": risk_score,
            "category": risk_category,
            "assessment_date": datetime.now().isoformat(),
        }

