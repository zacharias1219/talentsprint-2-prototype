"""
Response generator module.

Generates responses using RAG pipeline and fine-tuned model.
"""

from typing import Any, Dict, List, Optional

from src.model_training.inference import ModelInference
from src.rag_pipeline.query_understanding import QueryUnderstanding
from src.rag_pipeline.retriever import RAGRetriever
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ResponseGenerator:
    """Generates responses using RAG."""

    def __init__(self):
        """Initialize response generator."""
        self.query_understanding = QueryUnderstanding()
        self.retriever = RAGRetriever()
        self.model_inference = ModelInference()

    def generate_response(
        self,
        query: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate response to user query.

        Args:
            query: User query.
            user_id: Optional user ID for personalization.
            context: Optional additional context.

        Returns:
            Dictionary with response and metadata.
        """
        # Analyze query
        query_analysis = self.query_understanding.analyze_query(query)

        # Retrieve relevant context
        retrieved_docs = self.retriever.retrieve_context(query)

        # Build context string
        context_text = self._build_context(retrieved_docs, context)

        # Generate response using fine-tuned model
        prompt = self._build_prompt(query, context_text, query_analysis)
        response_text = self.model_inference.generate(prompt)

        # Extract sources
        sources = [doc.get("metadata", {}) for doc in retrieved_docs]

        return {
            "response_text": response_text,
            "query_analysis": query_analysis,
            "sources": sources,
            "confidence": 0.8,  # Placeholder
        }

    def _build_context(
        self,
        retrieved_docs: List[Dict[str, Any]],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Build context string from retrieved documents.

        Args:
            retrieved_docs: Retrieved documents.
            additional_context: Optional additional context.

        Returns:
            Context string.
        """
        context_parts = []

        # Add retrieved documents
        for doc in retrieved_docs:
            text = doc.get("text", "")
            if text:
                context_parts.append(text)

        # Add additional context
        if additional_context:
            if additional_context.get("user_profile"):
                context_parts.append(f"User profile: {additional_context['user_profile']}")
            if additional_context.get("market_data"):
                context_parts.append(f"Market data: {additional_context['market_data']}")

        return "\n\n".join(context_parts)

    def _build_prompt(
        self,
        query: str,
        context: str,
        query_analysis: Dict[str, Any],
    ) -> str:
        """
        Build prompt for model.

        Args:
            query: User query.
            context: Retrieved context.
            query_analysis: Query analysis results.

        Returns:
            Formatted prompt.
        """
        intent = query_analysis.get("intent", "general")

        prompt_parts = [
            "You are a financial advisor AI assistant. Provide helpful, accurate financial advice.",
            "",
            f"Context:",
            context,
            "",
            f"User Question: {query}",
            "",
            "Provide a clear, helpful response based on the context provided.",
        ]

        return "\n".join(prompt_parts)

