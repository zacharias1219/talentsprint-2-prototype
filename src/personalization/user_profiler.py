"""
User profiler module.

Manages user profiles and profile data.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.utils.database import execute_query, execute_update
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserProfiler:
    """Manages user profiles."""

    def create_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create or update user profile.

        Args:
            user_id: User ID.
            profile_data: Profile data dictionary.

        Returns:
            Created profile dictionary.
        """
        # Check if profile exists
        existing = self.get_profile(user_id)
        if existing:
            return self.update_profile(user_id, profile_data)

        # Extract profile fields
        demographics = profile_data.get("demographics", {})
        risk_tolerance = profile_data.get("risk_tolerance", {})

        query = """
            INSERT INTO user_profiles (
                user_id, age, income, employment_status, location,
                risk_tolerance_score, risk_category, investment_experience,
                profile_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """

        params = (
            user_id,
            demographics.get("age"),
            demographics.get("income"),
            demographics.get("employment_status"),
            demographics.get("location"),
            risk_tolerance.get("score"),
            risk_tolerance.get("category"),
            profile_data.get("investment_experience"),
            profile_data,
        )

        result = execute_query(query, params, fetch_one=True)
        logger.info(f"Created profile for user {user_id}")
        return result

    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user profile.

        Args:
            user_id: User ID.

        Returns:
            Profile dictionary or None if not found.
        """
        query = "SELECT * FROM user_profiles WHERE user_id = %s"
        result = execute_query(query, (user_id,), fetch_one=True)
        return result

    def update_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update user profile.

        Args:
            user_id: User ID.
            profile_data: Updated profile data.

        Returns:
            Updated profile dictionary.
        """
        demographics = profile_data.get("demographics", {})
        risk_tolerance = profile_data.get("risk_tolerance", {})

        query = """
            UPDATE user_profiles
            SET age = %s, income = %s, employment_status = %s, location = %s,
                risk_tolerance_score = %s, risk_category = %s,
                investment_experience = %s, profile_data = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING *
        """

        params = (
            demographics.get("age"),
            demographics.get("income"),
            demographics.get("employment_status"),
            demographics.get("location"),
            risk_tolerance.get("score"),
            risk_tolerance.get("category"),
            profile_data.get("investment_experience"),
            profile_data,
            user_id,
        )

        result = execute_query(query, params, fetch_one=True)
        logger.info(f"Updated profile for user {user_id}")
        return result

