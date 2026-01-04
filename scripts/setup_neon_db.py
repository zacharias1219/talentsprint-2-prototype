"""
Setup script for Neon PostgreSQL database connection.

This script helps configure and test the Neon database connection for user authentication.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_neon_database():
    """Setup and test Neon database connection."""
    print("=" * 60)
    print("Neon Database Setup")
    print("=" * 60)
    
    # Get connection string from user
    print("\n📋 Please provide your Neon database connection string.")
    print("   You can find it in your Neon dashboard under 'Connection Details'")
    print("   Format: postgresql://user:password@host.neon.tech/dbname?sslmode=require\n")
    
    connection_string = input("Enter your Neon connection string: ").strip()
    
    if not connection_string:
        print("❌ Connection string is required!")
        return False
    
    # Validate connection string format
    if not connection_string.startswith("postgresql://"):
        print("⚠️  Warning: Connection string should start with 'postgresql://'")
        print("   Adding it automatically...")
        if connection_string.startswith("postgres://"):
            connection_string = connection_string.replace("postgres://", "postgresql://", 1)
        else:
            connection_string = "postgresql://" + connection_string
    
    # Ensure SSL mode is set
    if "sslmode" not in connection_string:
        separator = "&" if "?" in connection_string else "?"
        connection_string += f"{separator}sslmode=require"
    
    print(f"\n✅ Connection string configured: {connection_string[:50]}...")
    
    # Test connection
    print("\n🔌 Testing database connection...")
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        # Parse connection string
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected successfully!")
        print(f"   PostgreSQL version: {version['version'][:50]}...")
        
        # Initialize users table
        print("\n📊 Initializing users table...")
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
        
        # Create index
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_username_lower ON users(username_lower)")
        except:
            pass
        
        conn.commit()
        print("✅ Users table created successfully!")
        
        # Check if table exists
        cursor.execute("""
            SELECT COUNT(*) as count FROM information_schema.tables 
            WHERE table_name = 'users'
        """)
        table_exists = cursor.fetchone()['count'] > 0
        
        if table_exists:
            print("✅ Table verification successful!")
        
        cursor.close()
        conn.close()
        
        # Save to .env file
        env_file = project_root / ".env"
        print(f"\n💾 Saving configuration to {env_file}...")
        
        # Read existing .env if it exists
        env_vars = {}
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Update with new values
        env_vars['AUTH_STORAGE_TYPE'] = 'database'
        env_vars['DATABASE_URL'] = connection_string
        
        # Write back to .env
        with open(env_file, 'w') as f:
            f.write("# Database Configuration\n")
            f.write(f"AUTH_STORAGE_TYPE=database\n")
            f.write(f"DATABASE_URL={connection_string}\n")
            f.write("\n# Other environment variables\n")
            for key, value in env_vars.items():
                if key not in ['AUTH_STORAGE_TYPE', 'DATABASE_URL']:
                    f.write(f"{key}={value}\n")
        
        print("✅ Configuration saved to .env file!")
        print("\n" + "=" * 60)
        print("🎉 Setup Complete!")
        print("=" * 60)
        print("\nYour application is now configured to use Neon PostgreSQL.")
        print("You can now run: streamlit run ui/streamlit_app.py")
        print("\nNote: Make sure to add .env to .gitignore to keep your credentials safe!")
        
        return True
        
    except ImportError:
        print("❌ Error: psycopg2 is not installed!")
        print("   Install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your connection string is correct")
        print("2. Verify your Neon database is running")
        print("3. Check your network connection")
        print("4. Ensure your IP is whitelisted in Neon (if required)")
        return False


if __name__ == "__main__":
    success = setup_neon_database()
    sys.exit(0 if success else 1)

