"""
Security module for the Financial Advisor application.

Provides encryption, authentication, and data protection utilities.
"""

from .encryption import (
    ProfileEncryptor,
    get_encryptor,
    get_or_create_encryption_key,
    mask_sensitive_data,
    derive_key_from_password,
)

__all__ = [
    'ProfileEncryptor',
    'get_encryptor',
    'get_or_create_encryption_key',
    'mask_sensitive_data',
    'derive_key_from_password',
]


