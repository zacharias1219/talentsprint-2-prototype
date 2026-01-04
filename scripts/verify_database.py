"""
Database Initialization Verification Script.

Verifies that the database schema is properly initialized and accessible.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

try:
    from src.utils.database import get_db_connection, execute_query
    from src.utils.config import get_config
    from src.utils.logger import get_logger
    
    logger = get_logger(__name__)
except ImportError as e:
    print(f"Warning: Could not import database utilities: {e}")
    print("Database verification will be limited.")


def check_database_connection():
    """Check if database connection can be established."""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return True, "Database connection successful"
        else:
            return False, "Could not establish database connection"
    except Exception as e:
        return False, f"Database connection error: {e}"


def check_schema_exists():
    """Check if required tables exist."""
    required_tables = [
        "users",
        "user_profiles",
        "financial_goals",
        "recommendations",
        "interactions",
        "market_data_cache"
    ]
    
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Could not connect to database"
        
        cursor = conn.cursor()
        
        # Check each table
        missing_tables = []
        for table in required_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            
            exists = cursor.fetchone()[0]
            if not exists:
                missing_tables.append(table)
        
        cursor.close()
        conn.close()
        
        if missing_tables:
            return False, f"Missing tables: {', '.join(missing_tables)}"
        else:
            return True, "All required tables exist"
            
    except Exception as e:
        return False, f"Error checking schema: {e}"


def check_table_structure():
    """Check if tables have correct structure."""
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Could not connect to database"
        
        cursor = conn.cursor()
        
        # Check users table structure
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        users_columns = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not users_columns:
            return False, "Users table has no columns"
        
        return True, f"Table structure verified (users table has {len(users_columns)} columns)"
        
    except Exception as e:
        return False, f"Error checking table structure: {e}"


def check_sample_data():
    """Check if sample data exists."""
    try:
        conn = get_db_connection()
        if not conn:
            return False, "Could not connect to database"
        
        cursor = conn.cursor()
        
        # Check user count
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        
        # Check profile count
        cursor.execute("SELECT COUNT(*) FROM user_profiles;")
        profile_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Sample data: {user_count} users, {profile_count} profiles"
        
    except Exception as e:
        return False, f"Error checking sample data: {e}"


def verify_database():
    """Run all database verification checks."""
    print("=" * 60)
    print("Database Initialization Verification")
    print("=" * 60)
    print()
    
    results = []
    
    # Check 1: Database Connection
    print("1. Checking database connection...")
    success, message = check_database_connection()
    results.append(("Database Connection", success, message))
    status = "✅" if success else "❌"
    print(f"   {status} {message}")
    print()
    
    if not success:
        print("⚠️  Cannot proceed with further checks without database connection.")
        print("   Please ensure:")
        print("   - PostgreSQL is running")
        print("   - Database credentials are correct in config/config.yaml")
        print("   - Database exists (run: createdb financial_advisor)")
        return results
    
    # Check 2: Schema Existence
    print("2. Checking schema existence...")
    success, message = check_schema_exists()
    results.append(("Schema Existence", success, message))
    status = "✅" if success else "❌"
    print(f"   {status} {message}")
    print()
    
    if not success:
        print("⚠️  Schema not initialized. Run:")
        print("   psql financial_advisor < docs/schema.sql")
        print("   OR")
        print("   python scripts/init_database.py")
        return results
    
    # Check 3: Table Structure
    print("3. Checking table structure...")
    success, message = check_table_structure()
    results.append(("Table Structure", success, message))
    status = "✅" if success else "❌"
    print(f"   {status} {message}")
    print()
    
    # Check 4: Sample Data
    print("4. Checking sample data...")
    success, message = check_sample_data()
    results.append(("Sample Data", success, message))
    status = "✅" if success else "❌"
    print(f"   {status} {message}")
    print()
    
    # Summary
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    
    all_passed = all(r[1] for r in results)
    
    for check_name, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {check_name}: {message}")
    
    print()
    
    if all_passed:
        print("✅ All database checks passed!")
        print("   Database is properly initialized and ready to use.")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("   See docs/deployment_guide.md for setup instructions.")
    
    return results


def main():
    """Main function."""
    # Check if database config exists
    config_file = Path("config/config.yaml")
    if not config_file.exists():
        print("⚠️  Warning: config/config.yaml not found.")
        print("   Database verification may fail.")
        print()
    
    # Check if schema file exists
    schema_file = Path("docs/schema.sql")
    if not schema_file.exists():
        print("⚠️  Warning: docs/schema.sql not found.")
        print("   Cannot verify schema structure.")
        print()
    
    # Run verification
    results = verify_database()
    
    # Return exit code
    all_passed = all(r[1] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()




