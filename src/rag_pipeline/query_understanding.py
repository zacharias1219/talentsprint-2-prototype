"""
Query understanding module.

Analyzes user queries to extract intent and entities.
"""

import re
from typing import Any, Dict, List

from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueryUnderstanding:
    """Understands and analyzes user queries."""

    def __init__(self):
        """Initialize query understanding."""
        # Intent patterns
        self.intent_patterns = {
            "investment_advice": [
                r"invest",
                r"portfolio",
                r"stock",
                r"buy",
                r"recommend",
            ],
            "portfolio_review": [
                r"review",
                r"analyze",
                r"current",
                r"portfolio",
            ],
            "goal_planning": [
                r"goal",
                r"retirement",
                r"savings",
                r"plan",
            ],
            "market_analysis": [
                r"market",
                r"trend",
                r"analysis",
                r"forecast",
            ],
            "risk_assessment": [
                r"risk",
                r"safe",
                r"volatile",
            ],
        }

    def extract_intent(self, query: str) -> str:
        """
        Extract intent from query.

        Args:
            query: User query.

        Returns:
            Intent category.
        """
        query_lower = query.lower()

        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            if score > 0:
                intent_scores[intent] = score

        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general"

    def extract_entities(self, query: str) -> Dict[str, Any]:
        """
        Extract entities from query.

        Args:
            query: User query.

        Returns:
            Dictionary with extracted entities.
        """
        entities = {
            "instruments": [],
            "timeframes": [],
            "amounts": [],
            "goals": [],
        }

        # Extract stock symbols (uppercase 1-5 letter codes)
        symbols = re.findall(r"\b[A-Z]{1,5}\b", query)
        entities["instruments"] = [s for s in symbols if len(s) >= 1]

        # Extract timeframes
        timeframe_patterns = [
            r"(\d+)\s*(?:year|yr|month|mo|day|d)",
            r"(?:next|in)\s+(\d+)\s*(?:year|month)",
        ]
        for pattern in timeframe_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["timeframes"].extend(matches)

        # Extract amounts (dollar amounts)
        amount_patterns = [
            r"\$(\d+(?:,\d{3})*(?:\.\d{2})?)",
            r"(\d+(?:,\d{3})*)\s*dollars?",
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities["amounts"].extend([float(m.replace(",", "")) for m in matches])

        # Extract goals
        goal_keywords = ["retirement", "savings", "house", "education", "emergency"]
        for keyword in goal_keywords:
            if keyword.lower() in query.lower():
                entities["goals"].append(keyword)

        return entities

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze query comprehensively.

        Args:
            query: User query.

        Returns:
            Dictionary with query analysis results.
        """
        intent = self.extract_intent(query)
        entities = self.extract_entities(query)

        return {
            "original_query": query,
            "intent": intent,
            "entities": entities,
            "confidence": 0.8,  # Placeholder confidence score
        }

