"""
Safety filters module.

Filters content for safety and appropriateness.
"""

from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SafetyFilters:
    """Filters content for safety."""

    RISK_KEYWORDS = [
        "guaranteed returns",
        "risk-free",
        "get rich quick",
        "insider information",
    ]

    def filter_content(self, content: str) -> Dict[str, Any]:
        """
        Filter content for safety issues.

        Args:
            content: Content to filter.

        Returns:
            Filter result dictionary.
        """
        checks = []
        passed = True

        # Check for risky language
        risky_language = self._check_risky_language(content)
        checks.append({
            "check_type": "risky_language",
            "passed": not risky_language["found"],
            "message": risky_language["message"],
            "severity": "high" if risky_language["found"] else "low",
        })
        if risky_language["found"]:
            passed = False

        # Check for unrealistic expectations
        unrealistic = self._check_unrealistic_expectations(content)
        checks.append({
            "check_type": "unrealistic_expectations",
            "passed": not unrealistic["found"],
            "message": unrealistic["message"],
            "severity": "medium" if unrealistic["found"] else "low",
        })
        if unrealistic["found"]:
            passed = False

        return {
            "passed": passed,
            "checks": checks,
            "filtered_content": content,  # In production, would filter problematic parts
            "original_content": content,
        }

    def _check_risky_language(self, content: str) -> Dict[str, Any]:
        """Check for risky language."""
        content_lower = content.lower()
        found_keywords = [kw for kw in self.RISK_KEYWORDS if kw in content_lower]

        if found_keywords:
            return {
                "found": True,
                "message": f"Risky language detected: {', '.join(found_keywords)}",
            }
        return {"found": False, "message": "No risky language detected"}

    def _check_unrealistic_expectations(self, content: str) -> Dict[str, Any]:
        """Check for unrealistic expectations."""
        # Check for promises of high returns without risk
        if "guaranteed" in content.lower() and "return" in content.lower():
            return {
                "found": True,
                "message": "Unrealistic expectation: guaranteed returns",
            }
        return {"found": False, "message": "No unrealistic expectations detected"}

