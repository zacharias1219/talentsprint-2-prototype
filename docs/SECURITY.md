# Security Documentation

## Data Encryption

The Financial Advisor application encrypts all user profile data at rest using **Fernet symmetric encryption** from the `cryptography` library.

### How It Works

1. **Automatic Key Generation**: On first run, an encryption key is automatically generated and stored in `.encryption_key`
2. **Encrypted Storage**: User session files are saved with `.encrypted` extension instead of `.json`
3. **Transparent Decryption**: Data is automatically decrypted when loading sessions
4. **Migration**: Existing unencrypted files are automatically migrated to encrypted format

### What's Protected

- User profile information (age, income, savings)
- Financial goals and risk preferences
- Chat conversation history
- Portfolio recommendations

### Configuration

#### Development (Default)

No configuration needed. A key is auto-generated and stored in `.encryption_key`.

```
[Security] Generated new encryption key at .encryption_key
```

#### Production

For production, set the `ENCRYPTION_KEY` environment variable:

```bash
# Generate a new key in Python:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env file:
ENCRYPTION_KEY=your_generated_key_here
```

### Security Indicator

The app shows encryption status in the sidebar:
- 🔒 **Data encrypted at rest** - Encryption is active
- ⚠️ **Encryption not available** - Check cryptography installation

### Files Structure

```
data/
  user_sessions/
    session_name.encrypted    # Encrypted user data
    
.encryption_key               # Auto-generated key (development only)
```

### Best Practices

1. **Never commit `.encryption_key`** to version control
2. **Use environment variables** for production keys
3. **Backup encryption keys** securely (loss = data loss)
4. **Rotate keys periodically** for long-running deployments

### Manual Encryption/Decryption

```python
from src.security.encryption import ProfileEncryptor

# Encrypt data
encryptor = ProfileEncryptor()
encrypted = encryptor.encrypt_data({"name": "John", "income": 50000})

# Decrypt data
decrypted = encryptor.decrypt_data(encrypted)
```

### Password-Based Encryption

For additional security, you can derive keys from user passwords:

```python
from src.security.encryption import derive_key_from_password

# Derive key from password
key, salt = derive_key_from_password("user_password")

# Use derived key
encryptor = ProfileEncryptor(key=key)
```

### Masking Sensitive Data

For logging/display purposes:

```python
from src.security.encryption import mask_sensitive_data

profile = {"name": "John", "income": 150000, "ssn": "123-45-6789"}
masked = mask_sensitive_data(profile)
# {"name": "John", "income": "1****0", "ssn": "12*****89"}
```

## API Security

### Rate Limiting

API endpoints are rate-limited to 60 requests per minute per API key.

### Authentication

The REST API uses API key authentication:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/chat
```

## Compliance

### Disclaimers

All AI-generated advice includes compliance disclaimers:
- Not financial advice notice
- Recommendation to consult licensed advisors
- Past performance warnings

### Audit Logging

All advice given is logged to `logs/advice_audit/` for regulatory compliance.


