"""
Deployment script.

Prepares and deploys the application.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main deployment function."""
    logger.info("Starting deployment preparation...")

    # Check environment
    import os
    required_env_vars = [
        "ALPHA_VANTAGE_API_KEY",
        "PINECONE_API_KEY",
        "DATABASE_URL",
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        sys.exit(1)

    # Check database connection
    try:
        from src.utils.database import init_connection_pool
        init_connection_pool()
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        sys.exit(1)

    logger.info("Deployment preparation completed successfully!")
    logger.info("Run 'streamlit run ui/streamlit_app.py' to start the application")


if __name__ == "__main__":
    main()

