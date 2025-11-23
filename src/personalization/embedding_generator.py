"""
Embedding generator module.

Generates embeddings for user profiles and investment instruments.
"""

from typing import Any, Dict, List, Optional

import numpy as np
from sentence_transformers import SentenceTransformer

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generates embeddings for personalization."""

    def __init__(self):
        """Initialize embedding generator."""
        config = get_config()
        model_name = config.get("model.embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name} (dimension: {self.dimension})")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def generate_profile_embedding(
        self,
        profile_data: Dict[str, Any],
    ) -> List[float]:
        """
        Generate embedding for user profile.

        Args:
            profile_data: User profile data.

        Returns:
            Embedding vector.
        """
        # Convert profile to text representation
        text_parts = []

        demographics = profile_data.get("demographics", {})
        if demographics.get("age"):
            text_parts.append(f"Age: {demographics['age']}")
        if demographics.get("income"):
            text_parts.append(f"Income: ${demographics['income']:,.0f}")

        risk_tolerance = profile_data.get("risk_tolerance", {})
        if risk_tolerance.get("category"):
            text_parts.append(f"Risk tolerance: {risk_tolerance['category']}")

        if profile_data.get("investment_experience"):
            text_parts.append(f"Investment experience: {profile_data['investment_experience']}")

        # Add goals
        goals = profile_data.get("financial_goals", [])
        for goal in goals[:3]:  # Limit to first 3 goals
            text_parts.append(
                f"Goal: {goal.get('type', '')}, "
                f"Target: ${goal.get('target_amount', 0):,.0f}, "
                f"Timeframe: {goal.get('time_horizon', 0)} years"
            )

        profile_text = " ".join(text_parts)

        # Generate embedding
        embedding = self.model.encode(profile_text, convert_to_numpy=True)
        return embedding.tolist()

    def generate_instrument_embedding(
        self,
        instrument_data: Dict[str, Any],
    ) -> List[float]:
        """
        Generate embedding for investment instrument.

        Args:
            instrument_data: Instrument data dictionary.

        Returns:
            Embedding vector.
        """
        # Convert instrument to text
        text_parts = [
            f"Symbol: {instrument_data.get('symbol', '')}",
            f"Type: {instrument_data.get('type', '')}",
            f"Risk level: {instrument_data.get('risk_level', 'medium')}",
            f"Category: {instrument_data.get('category', '')}",
        ]

        if instrument_data.get("description"):
            text_parts.append(instrument_data["description"])

        instrument_text = " ".join(text_parts)

        # Generate embedding
        embedding = self.model.encode(instrument_text, convert_to_numpy=True)
        return embedding.tolist()

    def calculate_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float],
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector.
            embedding2: Second embedding vector.

        Returns:
            Similarity score between -1 and 1.
        """
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)
        return float(similarity)

