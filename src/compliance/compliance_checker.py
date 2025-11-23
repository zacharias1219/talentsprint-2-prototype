"""
Compliance checker module.

Ensures regulatory compliance and adds disclaimers.
"""

from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComplianceChecker:
    """Checks and enforces compliance."""

    DISCLAIMERS = [
        "This is not financial advice. Please consult a qualified financial advisor.",
        "Past performance does not guarantee future results.",
        "Investments carry risk of loss. Only invest what you can afford to lose.",
        "This information is for educational purposes only.",
        "Market conditions can change rapidly. Recommendations may become outdated.",
    ]

    def add_disclaimers(
        self,
        response: str,
        include_all: bool = False,
    ) -> str:
        """
        Add disclaimers to response.

        Args:
            response: Response text.
            include_all: If True, include all disclaimers. Otherwise, include primary ones.

        Returns:
            Response with disclaimers appended.
        """
        if include_all:
            disclaimers = self.DISCLAIMERS
        else:
            disclaimers = self.DISCLAIMERS[:2]  # Primary disclaimers

        disclaimer_text = "\n\n**Disclaimer:**\n" + "\n".join(f"- {d}" for d in disclaimers)

        return response + disclaimer_text

    def check_compliance(
        self,
        response: str,
        user_consent: bool = False,
    ) -> Dict[str, Any]:
        """
        Check response for compliance.

        Args:
            response: Response text.
            user_consent: Whether user has given consent.

        Returns:
            Compliance check result.
        """
        warnings = []

        # Check for unrealistic promises
        unrealistic_keywords = ["guaranteed", "risk-free", "always", "never lose"]
        for keyword in unrealistic_keywords:
            if keyword.lower() in response.lower():
                warnings.append(f"Unrealistic language detected: '{keyword}'")

        # Check user consent
        if not user_consent:
            warnings.append("User consent not obtained")

        return {
            "compliant": len(warnings) == 0,
            "warnings": warnings,
            "disclaimers_added": True,
        }

