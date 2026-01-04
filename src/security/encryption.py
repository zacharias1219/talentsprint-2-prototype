"""
Data Encryption Module for User Profile Protection.

Encrypts user financial data at rest using Fernet symmetric encryption.
The encryption key is derived from a master password or environment variable.
"""

import os
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_or_create_encryption_key() -> bytes:
    """
    Get encryption key from environment or generate a new one.
    
    For production, set ENCRYPTION_KEY in .env file.
    For development, a key will be auto-generated and stored.
    
    Returns:
        bytes: The Fernet encryption key
    """
    # Check for key in environment
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        return env_key.encode()
    
    # Check for stored key file
    key_file = Path(__file__).parent.parent.parent / ".encryption_key"
    
    if key_file.exists():
        return key_file.read_bytes()
    
    # Generate new key
    key = Fernet.generate_key()
    
    # Store it (in development only - production should use env var)
    key_file.write_bytes(key)
    print(f"[Security] Generated new encryption key at {key_file}")
    print("[Security] For production, move this to ENCRYPTION_KEY environment variable")
    
    return key


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """
    Derive an encryption key from a password using PBKDF2.
    
    Args:
        password: User-provided password
        salt: Optional salt (generated if not provided)
        
    Returns:
        Tuple of (key, salt)
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP recommended minimum
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


class ProfileEncryptor:
    """
    Handles encryption and decryption of user profile data.
    """
    
    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize the encryptor.
        
        Args:
            key: Optional encryption key. If not provided, uses default key.
        """
        if key is None:
            key = get_or_create_encryption_key()
        
        self.fernet = Fernet(key)
    
    def encrypt_data(self, data: Dict[str, Any]) -> bytes:
        """
        Encrypt a dictionary of user data.
        
        Args:
            data: Dictionary containing user profile data
            
        Returns:
            Encrypted bytes
        """
        # Convert to JSON string
        json_data = json.dumps(data, default=str)
        
        # Encrypt
        encrypted = self.fernet.encrypt(json_data.encode('utf-8'))
        
        return encrypted
    
    def decrypt_data(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Decrypt encrypted user data.
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted dictionary
            
        Raises:
            InvalidToken: If decryption fails (wrong key or corrupted data)
        """
        try:
            # Decrypt
            decrypted = self.fernet.decrypt(encrypted_data)
            
            # Parse JSON
            data = json.loads(decrypted.decode('utf-8'))
            
            return data
        except InvalidToken:
            raise ValueError("Decryption failed: Invalid key or corrupted data")
        except json.JSONDecodeError:
            raise ValueError("Decryption succeeded but data is not valid JSON")
    
    def encrypt_to_file(self, data: Dict[str, Any], file_path: Path) -> None:
        """
        Encrypt data and save to file.
        
        Args:
            data: Dictionary to encrypt
            file_path: Path to save encrypted data
        """
        encrypted = self.encrypt_data(data)
        
        # Save with .encrypted extension
        file_path = Path(str(file_path).replace('.json', '.encrypted'))
        file_path.write_bytes(encrypted)
    
    def decrypt_from_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and decrypt data from file.
        
        Args:
            file_path: Path to encrypted file
            
        Returns:
            Decrypted dictionary
        """
        # Handle both .encrypted and .json extensions
        encrypted_path = Path(str(file_path).replace('.json', '.encrypted'))
        
        if encrypted_path.exists():
            encrypted_data = encrypted_path.read_bytes()
            return self.decrypt_data(encrypted_data)
        elif file_path.exists():
            # Fallback to unencrypted file (for migration)
            with open(file_path, 'r') as f:
                return json.load(f)
        else:
            raise FileNotFoundError(f"No encrypted or plain file found at {file_path}")
    
    def migrate_to_encrypted(self, source_dir: Path) -> int:
        """
        Migrate existing JSON files to encrypted format.
        
        Args:
            source_dir: Directory containing .json files
            
        Returns:
            Number of files migrated
        """
        migrated = 0
        
        for json_file in source_dir.glob("*.json"):
            encrypted_file = json_file.with_suffix('.encrypted')
            
            # Skip if already encrypted
            if encrypted_file.exists():
                continue
            
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                self.encrypt_to_file(data, json_file)
                migrated += 1
                
                # Optionally delete original (uncomment for production)
                # json_file.unlink()
                
            except Exception as e:
                print(f"[Security] Failed to migrate {json_file}: {e}")
        
        return migrated


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Mask sensitive fields for logging/display purposes.
    
    Args:
        data: User profile data
        
    Returns:
        Copy of data with sensitive fields masked
    """
    masked = data.copy()
    
    sensitive_fields = ['income', 'savings', 'ssn', 'account_number', 'password']
    
    for field in sensitive_fields:
        if field in masked:
            value = masked[field]
            if isinstance(value, (int, float)):
                # Show only first digit and last digit for numbers
                str_val = str(int(value))
                if len(str_val) > 2:
                    masked[field] = f"{str_val[0]}{'*' * (len(str_val)-2)}{str_val[-1]}"
            elif isinstance(value, str) and len(value) > 4:
                # Show first and last 2 characters for strings
                masked[field] = f"{value[:2]}{'*' * (len(value)-4)}{value[-2:]}"
    
    return masked


# Singleton instance for app-wide use
_encryptor: Optional[ProfileEncryptor] = None


def get_encryptor() -> ProfileEncryptor:
    """Get the global encryptor instance."""
    global _encryptor
    if _encryptor is None:
        _encryptor = ProfileEncryptor()
    return _encryptor


