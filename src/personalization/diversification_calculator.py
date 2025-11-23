"""
Diversification calculator module.

Calculates portfolio diversification metrics.
"""

from typing import Any, Dict, List

import numpy as np

from src.utils.logger import get_logger

logger = get_logger(__name__)


class DiversificationCalculator:
    """Calculates diversification metrics."""

    def calculate_diversification_score(
        self,
        portfolio: List[Dict[str, Any]],
    ) -> float:
        """
        Calculate portfolio diversification score (0.0 to 1.0).

        Args:
            portfolio: List of portfolio holdings with allocations.

        Returns:
            Diversification score between 0.0 and 1.0.
        """
        if not portfolio:
            return 0.0

        # Extract allocations
        allocations = [holding.get("allocation_percentage", 0.0) for holding in portfolio]
        allocations = np.array(allocations)

        # Normalize allocations
        total_allocation = allocations.sum()
        if total_allocation == 0:
            return 0.0

        allocations = allocations / total_allocation

        # Calculate Herfindahl-Hirschman Index (HHI)
        # Lower HHI = more diversified
        hhi = np.sum(allocations ** 2)

        # Convert HHI to diversification score (inverse relationship)
        # Perfect diversification (equal weights) = 1.0
        # Perfect concentration (single asset) = 0.0
        diversification_score = 1.0 - hhi

        return float(diversification_score)

    def calculate_sector_diversification(
        self,
        portfolio: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate sector diversification metrics.

        Args:
            portfolio: List of portfolio holdings with sector information.

        Returns:
            Dictionary with sector diversification metrics.
        """
        sector_allocations = {}

        for holding in portfolio:
            sector = holding.get("sector", "Unknown")
            allocation = holding.get("allocation_percentage", 0.0)
            sector_allocations[sector] = sector_allocations.get(sector, 0.0) + allocation

        # Calculate metrics
        num_sectors = len(sector_allocations)
        max_sector_allocation = max(sector_allocations.values()) if sector_allocations else 0.0

        return {
            "sector_allocations": sector_allocations,
            "num_sectors": num_sectors,
            "max_sector_allocation": max_sector_allocation,
            "is_diversified": max_sector_allocation < 0.4,  # No single sector > 40%
        }

    def calculate_geographic_diversification(
        self,
        portfolio: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Calculate geographic diversification metrics.

        Args:
            portfolio: List of portfolio holdings with geographic information.

        Returns:
            Dictionary with geographic diversification metrics.
        """
        geographic_allocations = {}

        for holding in portfolio:
            region = holding.get("region", "Unknown")
            allocation = holding.get("allocation_percentage", 0.0)
            geographic_allocations[region] = geographic_allocations.get(region, 0.0) + allocation

        num_regions = len(geographic_allocations)
        max_region_allocation = max(geographic_allocations.values()) if geographic_allocations else 0.0

        return {
            "geographic_allocations": geographic_allocations,
            "num_regions": num_regions,
            "max_region_allocation": max_region_allocation,
            "is_diversified": max_region_allocation < 0.5,  # No single region > 50%
        }

    def get_diversification_recommendations(
        self,
        portfolio: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Get diversification improvement recommendations.

        Args:
            portfolio: Current portfolio holdings.

        Returns:
            List of recommendation strings.
        """
        recommendations = []

        diversification_score = self.calculate_diversification_score(portfolio)
        sector_div = self.calculate_sector_diversification(portfolio)
        geo_div = self.calculate_geographic_diversification(portfolio)

        if diversification_score < 0.5:
            recommendations.append("Consider diversifying across more assets to reduce concentration risk")

        if not sector_div["is_diversified"]:
            recommendations.append(
                f"High concentration in {max(sector_div['sector_allocations'], key=sector_div['sector_allocations'].get)} sector. "
                "Consider adding exposure to other sectors."
            )

        if not geo_div["is_diversified"]:
            recommendations.append(
                f"High concentration in {max(geo_div['geographic_allocations'], key=geo_div['geographic_allocations'].get)} region. "
                "Consider adding international exposure."
            )

        if not recommendations:
            recommendations.append("Portfolio appears well-diversified")

        return recommendations

