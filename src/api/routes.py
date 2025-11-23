"""
API routes module.

Defines API endpoints for the financial advisor system.
"""

from typing import Any, Dict, List, Optional

from src.personalization.recommendation_engine import RecommendationEngine
from src.personalization.user_profiler import UserProfiler
from src.rag_pipeline.response_generator import ResponseGenerator
from src.utils.database import execute_query
from src.utils.logger import get_logger

logger = get_logger(__name__)


class APIRoutes:
    """API route handlers."""

    def __init__(self):
        """Initialize API routes."""
        self.user_profiler = UserProfiler()
        self.recommendation_engine = RecommendationEngine()
        self.response_generator = ResponseGenerator()

    def create_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create user profile.

        Args:
            user_id: User ID.
            profile_data: Profile data.

        Returns:
            Created profile.
        """
        return self.user_profiler.create_profile(user_id, profile_data)

    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile.

        Args:
            user_id: User ID.

        Returns:
            User profile or None.
        """
        return self.user_profiler.get_profile(user_id)

    def generate_recommendations(
        self,
        user_id: str,
        available_instruments: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations.

        Args:
            user_id: User ID.
            available_instruments: Available instruments.

        Returns:
            List of recommendations.
        """
        return self.recommendation_engine.generate_recommendations(
            user_id,
            available_instruments,
        )

    def chat_message(
        self,
        user_id: str,
        message: str,
    ) -> Dict[str, Any]:
        """
        Handle chat message.

        Args:
            user_id: User ID.
            message: User message.

        Returns:
            Response dictionary.
        """
        # Get user profile for context
        profile = self.user_profiler.get_profile(user_id)
        context = {"user_profile": profile} if profile else None

        # Generate response
        response = self.response_generator.generate_response(
            message,
            user_id=user_id,
            context=context,
        )

        # Store interaction
        self._store_interaction(user_id, message, response["response_text"])

        return response

    def _store_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
    ) -> None:
        """Store user interaction in database."""
        query_sql = """
            INSERT INTO interactions (user_id, query_text, response_text)
            VALUES (%s, %s, %s)
        """
        execute_query(query_sql, (user_id, query, response))

