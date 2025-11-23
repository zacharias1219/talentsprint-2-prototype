"""
Recommendation engine module.

Generates personalized investment recommendations.
"""

from typing import Any, Dict, List, Optional

from src.personalization.embedding_generator import EmbeddingGenerator
from src.personalization.user_profiler import UserProfiler
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RecommendationEngine:
    """Generates personalized recommendations."""

    def __init__(self):
        """Initialize recommendation engine."""
        self.embedding_generator = EmbeddingGenerator()
        self.user_profiler = UserProfiler()

    def generate_recommendations(
        self,
        user_id: str,
        available_instruments: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations.

        Args:
            user_id: User ID.
            available_instruments: List of available investment instruments.
            top_k: Number of top recommendations to return.

        Returns:
            List of recommendation dictionaries.
        """
        # Get user profile
        profile = self.user_profiler.get_profile(user_id)
        if not profile:
            logger.warning(f"No profile found for user {user_id}")
            return []

        profile_data = profile.get("profile_data", {})

        # Generate user profile embedding
        user_embedding = self.embedding_generator.generate_profile_embedding(profile_data)

        # Calculate similarities
        similarities = []
        for instrument in available_instruments:
            instrument_embedding = self.embedding_generator.generate_instrument_embedding(instrument)
            similarity = self.embedding_generator.calculate_similarity(
                user_embedding,
                instrument_embedding,
            )

            # Filter by risk category match
            risk_category = profile_data.get("risk_tolerance", {}).get("category", "moderate")
            instrument_risk = instrument.get("risk_level", "medium")

            # Risk matching bonus
            risk_match_bonus = 0.0
            if risk_category == "conservative" and instrument_risk in ["low", "medium"]:
                risk_match_bonus = 0.1
            elif risk_category == "moderate" and instrument_risk == "medium":
                risk_match_bonus = 0.1
            elif risk_category == "aggressive" and instrument_risk in ["medium", "high"]:
                risk_match_bonus = 0.1

            adjusted_similarity = similarity + risk_match_bonus

            similarities.append({
                "instrument": instrument,
                "similarity": adjusted_similarity,
                "base_similarity": similarity,
            })

        # Sort by similarity
        similarities.sort(key=lambda x: x["similarity"], reverse=True)

        # Generate recommendations
        recommendations = []
        for item in similarities[:top_k]:
            instrument = item["instrument"]
            recommendation = {
                "instrument": instrument.get("symbol"),
                "instrument_name": instrument.get("name", instrument.get("symbol")),
                "instrument_type": instrument.get("type"),
                "similarity_score": item["similarity"],
                "reasoning": self._generate_reasoning(profile_data, instrument, item["similarity"]),
                "risk_level": instrument.get("risk_level"),
            }
            recommendations.append(recommendation)

        logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
        return recommendations

    def _generate_reasoning(
        self,
        profile_data: Dict[str, Any],
        instrument: Dict[str, Any],
        similarity: float,
    ) -> str:
        """
        Generate reasoning for recommendation.

        Args:
            profile_data: User profile data.
            instrument: Instrument data.
            similarity: Similarity score.

        Returns:
            Reasoning text.
        """
        risk_category = profile_data.get("risk_tolerance", {}).get("category", "moderate")
        reasoning_parts = []

        if similarity > 0.7:
            reasoning_parts.append("High alignment with your profile")
        elif similarity > 0.5:
            reasoning_parts.append("Good match for your investment profile")

        if instrument.get("risk_level") == risk_category:
            reasoning_parts.append(f"Matches your {risk_category} risk tolerance")

        if not reasoning_parts:
            reasoning_parts.append("Consider based on your investment goals")

        return ". ".join(reasoning_parts) + "."

