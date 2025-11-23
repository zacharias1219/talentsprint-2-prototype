"""
Sentiment analyzer module.

Analyzes sentiment of financial news using FinBERT or similar models.
"""

from typing import Any, Dict, List, Optional

import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Analyzer for financial news sentiment."""

    def __init__(self):
        """Initialize sentiment analyzer."""
        config = get_config()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Try to load FinBERT model
        model_name = "yiyanghkust/finbert-tone"  # FinBERT for financial sentiment
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Loaded FinBERT model on {self.device}")
        except Exception as e:
            logger.warning(f"Failed to load FinBERT model: {e}. Using simple sentiment analysis.")
            self.model = None
            self.tokenizer = None

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a text.

        Args:
            text: Text to analyze.

        Returns:
            Dictionary with sentiment score and label.
        """
        if not text or not text.strip():
            return {
                "sentiment_score": 0.0,
                "sentiment_label": "neutral",
                "confidence": 0.0,
            }

        if self.model is None:
            # Fallback to simple keyword-based sentiment
            return self._simple_sentiment(text)

        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            ).to(self.device)

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

            # FinBERT labels: ['positive', 'negative', 'neutral']
            scores = predictions[0].cpu().numpy()
            labels = ["positive", "negative", "neutral"]

            # Get predicted label
            predicted_idx = np.argmax(scores)
            predicted_label = labels[predicted_idx]
            confidence = float(scores[predicted_idx])

            # Calculate sentiment score (-1 to 1)
            sentiment_score = float(scores[0] - scores[1])  # positive - negative

            return {
                "sentiment_score": sentiment_score,
                "sentiment_label": predicted_label,
                "confidence": confidence,
                "probabilities": {
                    "positive": float(scores[0]),
                    "negative": float(scores[1]),
                    "neutral": float(scores[2]),
                },
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._simple_sentiment(text)

    def _simple_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based sentiment analysis fallback.

        Args:
            text: Text to analyze.

        Returns:
            Dictionary with sentiment score and label.
        """
        text_lower = text.lower()

        # Positive keywords
        positive_keywords = [
            "up", "rise", "gain", "profit", "growth", "bullish", "surge", "rally",
            "strong", "positive", "outperform", "beat", "exceed", "increase",
        ]

        # Negative keywords
        negative_keywords = [
            "down", "fall", "loss", "decline", "bearish", "drop", "plunge",
            "weak", "negative", "underperform", "miss", "decrease", "crash",
        ]

        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)

        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        else:
            sentiment_score = (positive_count - negative_count) / total_keywords
            if sentiment_score > 0.1:
                sentiment_label = "positive"
            elif sentiment_score < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"

        return {
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "confidence": abs(sentiment_score),
            "method": "keyword_based",
        }

    def analyze_news_articles(
        self,
        articles: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Analyze sentiment for multiple news articles.

        Args:
            articles: List of news article dictionaries.

        Returns:
            List of articles with added sentiment analysis.
        """
        analyzed_articles = []

        for article in articles:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = self.analyze_sentiment(text)

            # Add sentiment to article
            article_with_sentiment = article.copy()
            article_with_sentiment["sentiment_score"] = sentiment["sentiment_score"]
            article_with_sentiment["sentiment_label"] = sentiment["sentiment_label"]
            article_with_sentiment["sentiment_confidence"] = sentiment["confidence"]

            analyzed_articles.append(article_with_sentiment)

        logger.info(f"Analyzed sentiment for {len(analyzed_articles)} articles")
        return analyzed_articles

    def get_aggregate_sentiment(
        self,
        articles: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Get aggregate sentiment across multiple articles.

        Args:
            articles: List of articles with sentiment analysis.

        Returns:
            Dictionary with aggregate sentiment metrics.
        """
        if not articles:
            return {
                "average_sentiment": 0.0,
                "sentiment_label": "neutral",
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        sentiments = [article.get("sentiment_score", 0.0) for article in articles]
        labels = [article.get("sentiment_label", "neutral") for article in articles]

        average_sentiment = np.mean(sentiments)
        positive_count = labels.count("positive")
        negative_count = labels.count("negative")
        neutral_count = labels.count("neutral")

        # Determine overall label
        if average_sentiment > 0.1:
            overall_label = "positive"
        elif average_sentiment < -0.1:
            overall_label = "negative"
        else:
            overall_label = "neutral"

        return {
            "average_sentiment": float(average_sentiment),
            "sentiment_label": overall_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "total_articles": len(articles),
        }

