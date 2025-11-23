"""
Database initialization script.

Creates database schema and initializes tables.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from src.utils.config import get_config
from src.utils.logger import get_logger

logger = get_logger(__name__)


def init_database() -> None:
    """Initialize database schema."""
    config = get_config()
    db_url = config.get("database.url")

    if not db_url:
        logger.error("Database URL not configured")
        sys.exit(1)

    try:
        # Parse database URL
        # Format: postgresql://user:password@host:port/database
        import urllib.parse
        parsed = urllib.parse.urlparse(db_url)

        # Connect to PostgreSQL server (not specific database)
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            database="postgres",  # Connect to default database
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        db_name = parsed.path[1:]  # Remove leading '/'
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,),
        )

        if not cursor.fetchone():
            # Create database
            logger.info(f"Creating database: {db_name}")
            cursor.execute(f'CREATE DATABASE "{db_name}"')
        else:
            logger.info(f"Database {db_name} already exists")

        cursor.close()
        conn.close()

        # Connect to the target database
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Read and execute schema SQL
        schema_file = project_root / "docs" / "schema.sql"
        if not schema_file.exists():
            logger.error(f"Schema file not found: {schema_file}")
            sys.exit(1)

        logger.info(f"Reading schema from: {schema_file}")
        with open(schema_file, "r") as f:
            schema_sql = f.read()

        # Execute schema SQL
        logger.info("Executing schema SQL...")
        cursor.execute(schema_sql)
        conn.commit()

        logger.info("Database schema initialized successfully")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()

