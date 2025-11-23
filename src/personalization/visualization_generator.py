"""
Visualization generator module.

Generates charts and visualizations for recommendations.
"""

from typing import Any, Dict, List, Optional

import plotly.graph_objects as go
import plotly.express as px

from src.utils.logger import get_logger

logger = get_logger(__name__)


class VisualizationGenerator:
    """Generates visualizations for recommendations."""

    def generate_allocation_chart(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> go.Figure:
        """
        Generate portfolio allocation pie chart.

        Args:
            recommendations: List of recommendations.

        Returns:
            Plotly figure.
        """
        # Extract allocation data
        labels = []
        values = []

        for rec in recommendations:
            instrument_name = rec.get("instrument_name", rec.get("instrument", "Unknown"))
            allocation = rec.get("allocation_percentage", 0.0)
            if allocation > 0:
                labels.append(instrument_name)
                values.append(allocation)

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_layout(title="Portfolio Allocation")
        return fig

    def generate_risk_return_chart(
        self,
        recommendations: List[Dict[str, Any]],
    ) -> go.Figure:
        """
        Generate risk-return scatter chart.

        Args:
            recommendations: List of recommendations.

        Returns:
            Plotly figure.
        """
        instruments = []
        risks = []
        returns = []

        for rec in recommendations:
            instruments.append(rec.get("instrument_name", rec.get("instrument", "Unknown")))
            risks.append(rec.get("risk_score", 0.5))
            returns.append(rec.get("expected_return", 0.0))

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=risks,
                y=returns,
                mode="markers+text",
                text=instruments,
                textposition="top center",
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            title="Risk-Return Analysis",
            xaxis_title="Risk Score",
            yaxis_title="Expected Return (%)",
        )

        return fig

