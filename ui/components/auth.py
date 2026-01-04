"""
Authentication component for login and signup.

Handles user registration, login, and session management with proper security.
Supports both JSON file storage (development) and PostgreSQL (production).
"""

import streamlit as st
import json
import re
import bcrypt
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple


# Storage configuration - check environment variable
STORAGE_TYPE = os.getenv("AUTH_STORAGE_TYPE", "json")  # "json" or "database"

# User database file (for JSON storage)
USER_DB_DIR = Path(__file__).parent.parent.parent / "data" / "users"
USER_DB_DIR.mkdir(parents=True, exist_ok=True)
USER_DB_FILE = USER_DB_DIR / "users.json"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    if not username:
        return False, "Username is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 30:
        return False, "Username must be no more than 30 characters"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    if not email:
        return True, ""  # Email is optional
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid email format"
    
    return True, ""


def validate_password(password: str) -> Tuple[bool, str, Dict[str, bool]]:
    """
    Validate password strength.
    
    Returns:
        (is_valid: bool, error_message: str, requirements_met: dict)
    """
    requirements = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "lowercase": bool(re.search(r'[a-z]', password)),
        "number": bool(re.search(r'[0-9]', password)),
    }
    
    if not password:
        return False, "Password is required", requirements
    
    if len(password) > 128:
        return False, "Password must be no more than 128 characters", requirements
    
    all_met = all(requirements.values())
    
    if not all_met:
        missing = [k for k, v in requirements.items() if not v]
        if "length" in missing:
            return False, "Password must be at least 8 characters", requirements
        elif "uppercase" in missing:
            return False, "Password must contain at least one uppercase letter", requirements
        elif "lowercase" in missing:
            return False, "Password must contain at least one lowercase letter", requirements
        elif "number" in missing:
            return False, "Password must contain at least one number", requirements
    
    return True, "", requirements


# ============================================================================
# JSON STORAGE (Development)
# ============================================================================

def load_users_json() -> Dict[str, Dict]:
    """Load users from JSON file."""
    if USER_DB_FILE.exists():
        try:
            with open(USER_DB_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
        except Exception:
            return {}
    return {}


def save_users_json(users: Dict[str, Dict]) -> None:
    """Save users to JSON file."""
    try:
        # Create backup before writing
        if USER_DB_FILE.exists():
            backup_file = USER_DB_FILE.with_suffix('.json.bak')
            import shutil
            shutil.copy2(USER_DB_FILE, backup_file)
        
        with open(USER_DB_FILE, 'w') as f:
            json.dump(users, f, indent=2)
    except Exception as e:
        st.error(f"Error saving user data: {str(e)}")


# ============================================================================
# DATABASE STORAGE (Production)
# ============================================================================

def get_db_connection():
    """Get database connection for user storage."""
    try:
        from src.utils.database import get_db_connection as get_conn
        return get_conn()
    except ImportError:
        return None
    except Exception:
        return None


def init_users_table():
    """Initialize users table in database if it doesn't exist."""
    try:
        # Direct database connection to avoid config dependencies
        import psycopg2
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return False
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Create table
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
        
        # Create index separately
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_username_lower ON users(username_lower)")
        except:
            pass  # Index might already exist
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        # Don't show error in UI, just return False
        return False


def load_users_db() -> Dict[str, Dict]:
    """Load users from database."""
    try:
        # Direct database connection to avoid config dependencies
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return {}
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        users = {}
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        if results:
            for row in results:
                user_key = row['username_lower']
                users[user_key] = {
                    "username": row['username'],
                    "password_hash": row['password_hash'],
                    "email": row.get('email', ''),
                    "created_at": row['created_at'].isoformat() if row['created_at'] else None,
                    "last_login": row['last_login'].isoformat() if row['last_login'] else None,
                    "failed_login_attempts": row.get('failed_login_attempts', 0),
                    "account_locked": row.get('account_locked', False)
                }
        
        cursor.close()
        conn.close()
        return users
    except Exception as e:
        # Silently fail and return empty dict
        return {}


def save_user_db(user_key: str, user_data: Dict) -> bool:
    """Save or update a user in database."""
    try:
        # Direct database connection to avoid config dependencies
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            return False
        
        # Helper to parse datetime strings
        def parse_datetime(dt_str):
            if not dt_str:
                return None
            if isinstance(dt_str, str):
                try:
                    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                except:
                    return None
            return dt_str
        
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE username_lower = %s", (user_key,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing user
            cursor.execute(
                """UPDATE users SET 
                    password_hash = %s, 
                    email = %s, 
                    last_login = %s,
                    failed_login_attempts = %s,
                    account_locked = %s
                WHERE username_lower = %s""",
                (
                    user_data['password_hash'],
                    user_data.get('email', ''),
                    parse_datetime(user_data.get('last_login')),
                    user_data.get('failed_login_attempts', 0),
                    user_data.get('account_locked', False),
                    user_key
                )
            )
        else:
            # Insert new user
            created_at = parse_datetime(user_data.get('created_at')) or datetime.now()
            cursor.execute(
                """INSERT INTO users 
                    (username, username_lower, password_hash, email, created_at, 
                     last_login, failed_login_attempts, account_locked)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    user_data['username'],
                    user_key,
                    user_data['password_hash'],
                    user_data.get('email', ''),
                    created_at,
                    parse_datetime(user_data.get('last_login')),
                    user_data.get('failed_login_attempts', 0),
                    user_data.get('account_locked', False)
                )
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        # Don't show error in UI, just return False
        return False


# ============================================================================
# UNIFIED STORAGE INTERFACE
# ============================================================================

def load_users() -> Dict[str, Dict]:
    """Load users from configured storage."""
    if STORAGE_TYPE == "database":
        # Initialize table if needed
        if "users_table_initialized" not in st.session_state:
            init_users_table()
            st.session_state.users_table_initialized = True
        return load_users_db()
    else:
        return load_users_json()


def save_user(user_key: str, user_data: Dict) -> bool:
    """Save user to configured storage."""
    if STORAGE_TYPE == "database":
        return save_user_db(user_key, user_data)
    else:
        users = load_users_json()
        users[user_key] = user_data
        save_users_json(users)
        return True


def register_user(username: str, password: str, email: str = "") -> Tuple[bool, str]:
    """
    Register a new user.
    
    Returns:
        (success: bool, message: str)
    """
    # Validate username
    username_valid, username_error = validate_username(username)
    if not username_valid:
        return False, username_error
    
    # Validate password
    password_valid, password_error, _ = validate_password(password)
    if not password_valid:
        return False, password_error
    
    # Validate email
    email_valid, email_error = validate_email(email)
    if not email_valid:
        return False, email_error
    
    users = load_users()
    user_key = username.lower().strip()
    
    if user_key in users:
        return False, "Username already exists"
    
    # Check if email is already registered (if provided)
    if email:
        for existing_user in users.values():
            if existing_user.get("email", "").lower() == email.lower().strip():
                return False, "Email is already registered"
    
    user_data = {
        "username": username.strip(),
        "password_hash": hash_password(password),
        "email": email.strip() if email else "",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "failed_login_attempts": 0,
        "account_locked": False
    }
    
    if save_user(user_key, user_data):
        return True, "Account created successfully!"
    else:
        return False, "Error creating account. Please try again."


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Authenticate a user.
    
    Returns:
        (success: bool, user_data: Optional[Dict], message: str)
    """
    if not username or not password:
        return False, None, "Username and password are required"
    
    users = load_users()
    user_key = username.lower().strip()
    
    if user_key not in users:
        return False, None, "Invalid username or password"
    
    user = users[user_key]
    
    # Check if account is locked
    if user.get("account_locked", False):
        return False, None, "Account is locked. Please contact support."
    
    # Verify password
    if not verify_password(password, user["password_hash"]):
        # Increment failed login attempts
        user["failed_login_attempts"] = user.get("failed_login_attempts", 0) + 1
        
        # Lock account after 5 failed attempts
        if user["failed_login_attempts"] >= 5:
            user["account_locked"] = True
            save_user(user_key, user)
            return False, None, "Account locked due to multiple failed login attempts. Please contact support."
        
        save_user(user_key, user)
        remaining_attempts = 5 - user["failed_login_attempts"]
        return False, None, f"Invalid username or password. {remaining_attempts} attempts remaining."
    
    # Successful login - reset failed attempts
    user["failed_login_attempts"] = 0
    user["account_locked"] = False
    user["last_login"] = datetime.now().isoformat()
    save_user(user_key, user)
    
    # Return user data (without password hash)
    user_data = {
        "username": user["username"],
        "email": user.get("email", ""),
        "created_at": user.get("created_at"),
        "last_login": user["last_login"]
    }
    
    return True, user_data, "Login successful!"


def render_login_signup():
    """Render login/signup interface with real-time validation."""
    st.title("🔐 AI Financial Advisor")
    st.caption("Sign in to access your personalized financial dashboard")
    
    # Show storage type indicator
    if STORAGE_TYPE == "database":
        st.caption("🔒 Production Mode: Database Storage")
    else:
        st.caption("📁 Development Mode: File Storage")
    
    # Initialize auth state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    
    # If already authenticated, show logout option
    if st.session_state.authenticated:
        st.success(f"✅ Logged in as **{st.session_state.current_user['username']}**")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.session_id = None
            st.session_state.user_profile = None
            st.session_state.user_recommendation = None
            st.session_state.messages = []
            st.rerun()
        return
    
    # Tabs for Login and Sign Up
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                help="Enter your registered username",
                key="login_username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                help="Enter your account password",
                key="login_password"
            )
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                # Real-time validation
                if not username:
                    st.error("Username is required")
                elif not password:
                    st.error("Password is required")
                else:
                    success, user_data, message = authenticate_user(username, password)
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user_data
                        st.session_state.session_id = user_data["username"]
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("signup_form", clear_on_submit=False):
            new_username = st.text_input(
                "Username",
                placeholder="Choose a username (3-30 characters, alphanumeric and underscores only)",
                help="3-30 characters, letters, numbers, and underscores only",
                key="signup_username"
            )
            new_email = st.text_input(
                "Email",
                placeholder="your.email@example.com",
                help="Optional: Your email address for account recovery",
                key="signup_email"
            )
            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter a strong password",
                help="Minimum 8 characters, must include uppercase, lowercase, and number",
                key="signup_password"
            )
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="signup_confirm_password"
            )
            submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            # Real-time password validation display
            if new_password:
                _, _, requirements = validate_password(new_password)
                with st.expander("Password Requirements", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("✅" if requirements["length"] else "❌", "At least 8 characters")
                        st.write("✅" if requirements["uppercase"] else "❌", "One uppercase letter")
                    with col2:
                        st.write("✅" if requirements["lowercase"] else "❌", "One lowercase letter")
                        st.write("✅" if requirements["number"] else "❌", "One number")
            
            if submit:
                # Real-time validation feedback
                validation_errors = []
                
                # Validate username
                username_valid, username_error = validate_username(new_username)
                if not username_valid:
                    validation_errors.append(f"Username: {username_error}")
                
                # Validate email
                email_valid, email_error = validate_email(new_email)
                if not email_valid:
                    validation_errors.append(f"Email: {email_error}")
                
                # Validate password
                password_valid, password_error, _ = validate_password(new_password)
                if not password_valid:
                    validation_errors.append(f"Password: {password_error}")
                
                # Check password match
                if new_password != confirm_password:
                    validation_errors.append("Passwords do not match")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    success, message = register_user(new_username, new_password, new_email)
                    if success:
                        st.success(message)
                        st.info("You can now login with your credentials")
                    else:
                        st.error(message)
