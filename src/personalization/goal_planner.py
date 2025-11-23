"""
Goal planner module.

Provides goal-based financial planning functionality.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.utils.database import execute_query
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GoalPlanner:
    """Provides goal-based planning."""

    def create_goal(
        self,
        user_id: str,
        goal_type: str,
        target_amount: float,
        time_horizon: int,
        priority: str = "medium",
    ) -> Dict[str, Any]:
        """
        Create a financial goal.

        Args:
            user_id: User ID.
            goal_type: Type of goal ('retirement', 'savings', 'house', etc.).
            target_amount: Target amount in dollars.
            time_horizon: Time horizon in years.
            priority: Priority level ('high', 'medium', 'low').

        Returns:
            Created goal dictionary.
        """
        query = """
            INSERT INTO financial_goals (
                user_id, goal_type, target_amount, time_horizon, priority
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """

        result = execute_query(query, (user_id, goal_type, target_amount, time_horizon, priority), fetch_one=True)
        logger.info(f"Created goal for user {user_id}: {goal_type}")
        return result

    def get_user_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all goals for a user.

        Args:
            user_id: User ID.

        Returns:
            List of goal dictionaries.
        """
        query = "SELECT * FROM financial_goals WHERE user_id = %s AND status = 'active' ORDER BY priority DESC"
        results = execute_query(query, (user_id,))
        return results or []

    def calculate_monthly_contribution(
        self,
        target_amount: float,
        time_horizon_years: int,
        current_amount: float = 0.0,
        expected_return: float = 0.07,
    ) -> float:
        """
        Calculate required monthly contribution to reach goal.

        Args:
            target_amount: Target amount.
            time_horizon_years: Time horizon in years.
            current_amount: Current amount saved.
            expected_return: Expected annual return (default 7%).

        Returns:
            Required monthly contribution.
        """
        # Future value of current amount
        months = time_horizon_years * 12
        monthly_rate = expected_return / 12

        future_value_current = current_amount * ((1 + monthly_rate) ** months)

        # Remaining amount needed
        remaining = target_amount - future_value_current

        if remaining <= 0:
            return 0.0

        # Calculate monthly payment using annuity formula
        if monthly_rate == 0:
            monthly_contribution = remaining / months
        else:
            monthly_contribution = remaining * monthly_rate / (((1 + monthly_rate) ** months) - 1)

        return max(0.0, monthly_contribution)

    def generate_goal_plan(
        self,
        user_id: str,
        goal_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate a plan for achieving a goal.

        Args:
            user_id: User ID.
            goal_id: Optional specific goal ID. If None, uses all active goals.

        Returns:
            Goal plan dictionary.
        """
        if goal_id:
            query = "SELECT * FROM financial_goals WHERE goal_id = %s AND user_id = %s"
            goals = execute_query(query, (goal_id, user_id))
        else:
            goals = self.get_user_goals(user_id)

        plans = []
        for goal in goals:
            target_amount = float(goal["target_amount"])
            time_horizon = goal["time_horizon"]
            current_progress = float(goal.get("current_progress", 0.0))

            monthly_contribution = self.calculate_monthly_contribution(
                target_amount,
                time_horizon,
                current_progress,
            )

            progress_percentage = (current_progress / target_amount * 100) if target_amount > 0 else 0.0

            plan = {
                "goal_id": goal["goal_id"],
                "goal_type": goal["goal_type"],
                "target_amount": target_amount,
                "current_progress": current_progress,
                "progress_percentage": progress_percentage,
                "time_horizon_years": time_horizon,
                "required_monthly_contribution": monthly_contribution,
                "priority": goal["priority"],
            }

            plans.append(plan)

        return {
            "user_id": user_id,
            "goals": plans,
            "total_monthly_contribution": sum(p["required_monthly_contribution"] for p in plans),
        }

    def update_goal_progress(
        self,
        goal_id: int,
        current_progress: float,
    ) -> Dict[str, Any]:
        """
        Update goal progress.

        Args:
            goal_id: Goal ID.
            current_progress: Current progress amount.

        Returns:
            Updated goal dictionary.
        """
        query = """
            UPDATE financial_goals
            SET current_progress = %s, updated_at = CURRENT_TIMESTAMP
            WHERE goal_id = %s
            RETURNING *
        """

        result = execute_query(query, (current_progress, goal_id), fetch_one=True)
        logger.info(f"Updated progress for goal {goal_id}")
        return result

