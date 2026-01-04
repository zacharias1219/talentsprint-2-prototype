"""
Quick Neon setup - just provide the connection string as argument.
Usage: python scripts/quick_neon_setup.py "postgresql://user:pass@host.neon.tech/dbname"
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent

def quick_setup(connection_string: str):
    """Quick setup with connection string."""
    if not connection_string:
        print("❌ Connection string required!")
        return False
    
    # Ensure proper format
    if not connection_string.startswith("postgresql://"):
        if connection_string.startswith("postgres://"):
            connection_string = connection_string.replace("postgres://", "postgresql://", 1)
        else:
            connection_string = "postgresql://" + connection_string
    
    # Ensure SSL mode
    if "sslmode" not in connection_string:
        separator = "&" if "?" in connection_string else "?"
        connection_string += f"{separator}sslmode=require"
    
    # Test connection
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("🔌 Testing connection...")
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Initialize table
        print("📊 Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(30) UNIQUE NOT NULL,
                username_lower VARCHAR(30) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                failed_login_attempts INTEGER DEFAULT 0,
                account_locked BOOLEAN DEFAULT FALSE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_username_lower ON users(username_lower)")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Save to .env
        env_file = project_root / ".env"
        with open(env_file, 'w') as f:
            f.write("# Database Configuration\n")
            f.write("AUTH_STORAGE_TYPE=database\n")
            f.write(f"DATABASE_URL={connection_string}\n")
        
        print("✅ Setup complete! Configuration saved to .env")
        print("✅ Users table initialized in Neon database")
        return True
        
    except ImportError:
        print("❌ Install psycopg2-binary: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/quick_neon_setup.py \"postgresql://user:pass@host.neon.tech/dbname\"")
        sys.exit(1)
    
    connection_string = sys.argv[1]
    success = quick_setup(connection_string)
    sys.exit(0 if success else 1)

