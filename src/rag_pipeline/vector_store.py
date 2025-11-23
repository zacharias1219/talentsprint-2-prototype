"""
Vector store module for Pinecone integration.

Manages vector embeddings in Pinecone.
"""

from typing import Any, Dict, List, Optional

import pinecone
from langchain.vectorstores import Pinecone as LangChainPinecone
from langchain.embeddings import HuggingFaceEmbeddings

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Manages vector store operations."""

    def __init__(self):
        """Initialize vector store."""
        config = get_config()
        pinecone_config = config.get("pinecone", {})

        api_key = pinecone_config.get("api_key")
        environment = pinecone_config.get("environment")
        index_name = pinecone_config.get("index_name", "financial-advisor")

        if not api_key:
            raise ValueError("Pinecone API key not configured")

        # Initialize Pinecone
        try:
            # Pinecone v2+ initialization
            pc = pinecone.Pinecone(api_key=api_key)
            self.index = pc.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
        except Exception as e:
            # Fallback to v1 initialization
            try:
                pinecone.init(api_key=api_key, environment=environment)
                self.index = pinecone.Index(index_name)
                logger.info(f"Connected to Pinecone index: {index_name} (v1)")
            except Exception as e2:
                logger.error(f"Failed to initialize Pinecone: {e2}")
                raise

        # Initialize embeddings
        embedding_model = config.get("model.embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Add documents to vector store.

        Args:
            texts: List of text documents.
            metadatas: Optional list of metadata dictionaries.

        Returns:
            List of document IDs.
        """
        try:
            # Generate embeddings
            embeddings = self.embeddings.embed_documents(texts)

            # Prepare vectors
            vectors = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                vector_id = f"doc_{i}"
                metadata = metadatas[i] if metadatas else {}
                metadata["text"] = text
                vectors.append((vector_id, embedding, metadata))

            # Upsert to Pinecone
            self.index.upsert(vectors=vectors)
            logger.info(f"Added {len(vectors)} documents to vector store")

            return [v[0] for v in vectors]

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Search query.
            top_k: Number of results to return.
            filter_dict: Optional metadata filter.

        Returns:
            List of search results with metadata.
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)

            # Query Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict,
            )

            # Format results
            formatted_results = []
            for match in results.get("matches", []):
                formatted_results.append({
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "text": match.get("metadata", {}).get("text", ""),
                    "metadata": match.get("metadata", {}),
                })

            logger.debug(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search vector store: {e}")
            raise

