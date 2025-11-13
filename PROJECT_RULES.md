# PROJECT RULES & GUIDELINES
## AI-Powered Financial Advisor - Implementation Standards

**Version:** 1.0  
**Last Updated:** January 2025  
**Purpose:** Comprehensive rules and guidelines to ensure consistent, secure, and high-quality implementation

---

## TABLE OF CONTENTS
1. [Code Formatting & Style](#code-formatting--style)
2. [Security Requirements](#security-requirements)
3. [Framework-Specific Rules](#framework-specific-rules)
4. [Database Standards](#database-standards)
5. [API Integration Rules](#api-integration-rules)
6. [Error Handling & Logging](#error-handling--logging)
7. [Testing Requirements](#testing-requirements)
8. [Documentation Standards](#documentation-standards)
9. [Data Handling & Privacy](#data-handling--privacy)
10. [Compliance & Regulatory](#compliance--regulatory)
11. [Performance Standards](#performance-standards)
12. [Code Review Checklist](#code-review-checklist)

---

## CODE FORMATTING & STYLE

### Python Style Guide
- **PEP 8 Compliance:** All code MUST follow PEP 8 style guide
- **Line Length:** Maximum 100 characters per line (hard limit: 120)
- **Indentation:** Use 4 spaces (NO tabs)
- **Imports:** 
  - Group imports: standard library, third-party, local
  - One import per line
  - Alphabetical order within groups
  - Use absolute imports, not relative
  ```python
  # Standard library
  import os
  import sys
  from datetime import datetime
  from typing import Dict, List, Optional
  
  # Third-party
  import pandas as pd
  import streamlit as st
  from langchain import LLMChain
  
  # Local
  from src.utils.config import load_config
  from src.utils.logger import get_logger
  ```

### Type Hints
- **MANDATORY:** All functions MUST have type hints
- **Return Types:** Always specify return types, use `None` if no return
- **Complex Types:** Use `typing` module (Dict, List, Optional, Union, Tuple)
- **Example:**
  ```python
  def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
      """Get user profile by ID."""
      pass
  ```

### Docstrings
- **Format:** Google-style docstrings
- **Required Sections:** Description, Args, Returns, Raises (if applicable)
- **Example:**
  ```python
  def calculate_risk_score(age: int, income: float, risk_tolerance: str) -> float:
      """
      Calculate risk tolerance score based on user demographics.
      
      Args:
          age: User's age in years
          income: Annual income in USD
          risk_tolerance: Risk category ('conservative', 'moderate', 'aggressive')
      
      Returns:
          Risk score between 0.0 and 1.0
      
      Raises:
          ValueError: If risk_tolerance is not a valid category
      """
      pass
  ```

### Naming Conventions
- **Variables/Functions:** `snake_case`
- **Classes:** `PascalCase`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private Methods:** `_leading_underscore`
- **File Names:** `snake_case.py`
- **Module Names:** `snake_case`

### Code Organization
- **File Structure:** One class per file (when possible)
- **Function Length:** Maximum 50 lines per function
- **Class Length:** Maximum 300 lines per class
- **Module Length:** Maximum 500 lines per module
- **Cyclomatic Complexity:** Maximum 10 per function

---

## SECURITY REQUIREMENTS

### API Key Management
- **NEVER** commit API keys to version control
- **ALWAYS** use environment variables via `.env` file
- **ALWAYS** validate API keys before use
- **ALWAYS** rotate keys if compromised
- **NEVER** log API keys or sensitive data
- **Example:**
  ```python
  import os
  from dotenv import load_dotenv
  
  load_dotenv()
  
  API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
  if not API_KEY:
      raise ValueError("ALPHA_VANTAGE_API_KEY not found in environment")
  ```

### Data Encryption
- **Sensitive Data:** Encrypt user financial data at rest
- **Transmission:** Use HTTPS/TLS for all API calls
- **Database:** Use encrypted connections (SSL)
- **Passwords:** Never store plain text passwords (use hashing)

### Input Validation
- **ALWAYS** validate all user inputs
- **ALWAYS** sanitize inputs before database queries (prevent SQL injection)
- **ALWAYS** validate API responses before processing
- **ALWAYS** check data types and ranges
- **Example:**
  ```python
  from pydantic import BaseModel, validator
  
  class UserProfile(BaseModel):
      age: int
      income: float
      
      @validator('age')
      def validate_age(cls, v):
          if not 18 <= v <= 100:
              raise ValueError('Age must be between 18 and 100')
          return v
      
      @validator('income')
      def validate_income(cls, v):
          if v < 0:
              raise ValueError('Income cannot be negative')
          return v
  ```

### SQL Injection Prevention
- **NEVER** use string concatenation for SQL queries
- **ALWAYS** use parameterized queries
- **ALWAYS** use ORM or query builders when possible
- **Example:**
  ```python
  # BAD - SQL Injection risk
  query = f"SELECT * FROM users WHERE user_id = '{user_id}'"
  
  # GOOD - Parameterized query
  query = "SELECT * FROM users WHERE user_id = %s"
  cursor.execute(query, (user_id,))
  ```

### Authentication & Authorization
- **ALWAYS** implement authentication for API endpoints
- **ALWAYS** verify user permissions before data access
- **ALWAYS** use secure session management
- **ALWAYS** implement rate limiting

### Secrets Management
- **NEVER** hardcode secrets
- **ALWAYS** use `.env` files (add to `.gitignore`)
- **ALWAYS** use different keys for dev/staging/production
- **ALWAYS** rotate secrets regularly

---

## FRAMEWORK-SPECIFIC RULES

### LangChain Rules
- **Version:** Use LangChain >= 0.1.0
- **Chains:** Use `LLMChain` or `RetrievalQA` chains
- **Prompts:** Store prompts in separate files or config
- **Memory:** Use `ConversationBufferMemory` for chat history
- **Error Handling:** Wrap LangChain calls in try-except blocks
- **Example:**
  ```python
  from langchain.chains import RetrievalQA
  from langchain.llms import OpenAI
  
  try:
      qa_chain = RetrievalQA.from_chain_type(
          llm=OpenAI(temperature=0),
          chain_type="stuff",
          retriever=retriever,
          return_source_documents=True
      )
      result = qa_chain({"query": user_query})
  except Exception as e:
      logger.error(f"LangChain error: {e}")
      raise
  ```

### Streamlit Rules
- **Session State:** Use `st.session_state` for state management
- **Caching:** Use `@st.cache_data` for data caching
- **Caching Models:** Use `@st.cache_resource` for model loading
- **Error Handling:** Display user-friendly error messages
- **Page Config:** Set page config at the top of the file
- **Example:**
  ```python
  import streamlit as st
  
  st.set_page_config(
      page_title="AI Financial Advisor",
      page_icon="💰",
      layout="wide"
  )
  
  @st.cache_data
  def load_market_data(symbol: str):
      """Load and cache market data."""
      return fetch_stock_data(symbol)
  
  if 'user_id' not in st.session_state:
      st.session_state.user_id = None
  ```

### FinGPT/Transformers Rules
- **Model Loading:** Load models once and cache them
- **Device Management:** Use `device_map="auto"` for GPU allocation
- **Memory Management:** Use `torch.float16` for memory efficiency
- **Error Handling:** Handle CUDA errors gracefully
- **Example:**
  ```python
  import torch
  from transformers import AutoTokenizer, AutoModelForCausalLM
  
  device = "cuda" if torch.cuda.is_available() else "cpu"
  
  model = AutoModelForCausalLM.from_pretrained(
      model_name,
      torch_dtype=torch.float16 if device == "cuda" else torch.float32,
      device_map="auto"
  )
  ```

### Pinecone Rules
- **Index Management:** Create index once, reuse connection
- **Batch Operations:** Use batch upsert for efficiency
- **Metadata Filtering:** Always use metadata filters when possible
- **Error Handling:** Handle rate limits and connection errors
- **Example:**
  ```python
  import pinecone
  
  pinecone.init(api_key=os.getenv('PINECONE_API_KEY'))
  index = pinecone.Index("financial-advisor")
  
  try:
      results = index.query(
          vector=query_vector,
          top_k=5,
          include_metadata=True,
          filter={"category": "investment_advice"}
      )
  except Exception as e:
      logger.error(f"Pinecone query error: {e}")
      raise
  ```

### Alpha Vantage API Rules
- **Rate Limiting:** ALWAYS implement rate limiting (5 calls/min)
- **Caching:** Cache responses to minimize API calls
- **Error Handling:** Handle API errors and retry with backoff
- **Data Validation:** Validate API responses before use
- **Example:**
  ```python
  import time
  from alpha_vantage.timeseries import TimeSeries
  
  class AlphaVantageClient:
      def __init__(self, api_key: str):
          self.ts = TimeSeries(key=api_key)
          self.last_call_time = 0
          self.min_interval = 12  # 5 calls per minute
      
      def get_stock_data(self, symbol: str) -> Dict:
          # Rate limiting
          elapsed = time.time() - self.last_call_time
          if elapsed < self.min_interval:
              time.sleep(self.min_interval - elapsed)
          
          try:
              data, meta = self.ts.get_daily(symbol=symbol)
              self.last_call_time = time.time()
              return data
          except Exception as e:
              logger.error(f"Alpha Vantage API error: {e}")
              raise
  ```

### Database (PostgreSQL) Rules
- **Connection Pooling:** Use connection pooling
- **Transactions:** Use transactions for multi-step operations
- **Error Handling:** Handle database errors gracefully
- **Connection Management:** Always close connections
- **Example:**
  ```python
  import psycopg2
  from psycopg2 import pool
  
  connection_pool = psycopg2.pool.SimpleConnectionPool(
      1, 20,
      host=DB_HOST,
      database=DB_NAME,
      user=DB_USER,
      password=DB_PASSWORD
  )
  
  def execute_query(query: str, params: Tuple) -> List[Dict]:
      conn = connection_pool.getconn()
      try:
          cursor = conn.cursor()
          cursor.execute(query, params)
          results = cursor.fetchall()
          conn.commit()
          return results
      except Exception as e:
          conn.rollback()
          logger.error(f"Database error: {e}")
          raise
      finally:
          connection_pool.putconn(conn)
  ```

---

## DATABASE STANDARDS

### Schema Design
- **Naming:** Use `snake_case` for table and column names
- **Primary Keys:** Always use `SERIAL` or `UUID` for primary keys
- **Foreign Keys:** Always define foreign key constraints
- **Indexes:** Create indexes on frequently queried columns
- **Timestamps:** Always include `created_at` and `updated_at` columns

### Query Optimization
- **SELECT:** Only select needed columns (avoid `SELECT *`)
- **JOINs:** Use appropriate JOIN types
- **WHERE:** Use indexed columns in WHERE clauses
- **LIMIT:** Always use LIMIT for large result sets
- **Transactions:** Use transactions for related operations

### Data Types
- **Money:** Use `DECIMAL(15, 2)` for financial amounts
- **Dates:** Use `TIMESTAMP` for timestamps
- **JSON:** Use `JSONB` for structured data
- **Text:** Use `TEXT` for long text, `VARCHAR(n)` for short text

---

## API INTEGRATION RULES

### HTTP Requests
- **Timeout:** Always set timeout (default: 30 seconds)
- **Retries:** Implement exponential backoff retry logic
- **Error Handling:** Handle HTTP errors (4xx, 5xx)
- **Headers:** Set appropriate headers (User-Agent, Content-Type)
- **Example:**
  ```python
  import requests
  from requests.adapters import HTTPAdapter
  from urllib3.util.retry import Retry
  
  session = requests.Session()
  retry_strategy = Retry(
      total=3,
      backoff_factor=1,
      status_forcelist=[429, 500, 502, 503, 504]
  )
  adapter = HTTPAdapter(max_retries=retry_strategy)
  session.mount("http://", adapter)
  session.mount("https://", adapter)
  
  response = session.get(url, timeout=30)
  ```

### Rate Limiting
- **Alpha Vantage:** 5 calls/minute, 500 calls/day
- **OpenAI:** Check rate limits per tier
- **Pinecone:** Check plan limits
- **Implementation:** Use token bucket or sliding window algorithm

### Caching
- **Cache Strategy:** Cache API responses based on data freshness needs
- **Cache Keys:** Use meaningful cache keys
- **Cache Invalidation:** Implement cache invalidation logic
- **TTL:** Set appropriate Time-To-Live for cached data

---

## ERROR HANDLING & LOGGING

### Error Handling
- **Specific Exceptions:** Catch specific exceptions, not bare `except:`
- **Error Messages:** Provide clear, actionable error messages
- **Error Logging:** Log errors with context
- **User Messages:** Display user-friendly error messages
- **Example:**
  ```python
  try:
      result = process_data(data)
  except ValueError as e:
      logger.error(f"Invalid data format: {e}", exc_info=True)
      raise ValueError("Please check your input data format")
  except ConnectionError as e:
      logger.error(f"Connection error: {e}", exc_info=True)
      raise ConnectionError("Unable to connect to service. Please try again later.")
  except Exception as e:
      logger.error(f"Unexpected error: {e}", exc_info=True)
      raise RuntimeError("An unexpected error occurred. Please contact support.")
  ```

### Logging Standards
- **Log Levels:** Use appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Log Format:** Include timestamp, level, module, message
- **Sensitive Data:** NEVER log passwords, API keys, or financial data
- **Structured Logging:** Use structured logging when possible
- **Example:**
  ```python
  import logging
  
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)
  
  formatter = logging.Formatter(
      '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )
  
  handler = logging.FileHandler('logs/app.log')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  
  logger.info("Processing user request", extra={"user_id": user_id})
  ```

---

## TESTING REQUIREMENTS

### Test Coverage
- **Minimum Coverage:** 80% code coverage
- **Critical Paths:** 100% coverage for critical functions
- **Test Types:** Unit tests, integration tests, end-to-end tests

### Unit Tests
- **Location:** `tests/unit/`
- **Naming:** `test_<function_name>.py`
- **Isolation:** Each test must be independent
- **Mocking:** Mock external dependencies
- **Example:**
  ```python
  import pytest
  from unittest.mock import Mock, patch
  
  def test_get_user_profile():
      with patch('src.utils.database.get_db_connection') as mock_db:
          mock_db.return_value.fetchone.return_value = {"user_id": "123"}
          result = get_user_profile("123")
          assert result["user_id"] == "123"
  ```

### Integration Tests
- **Location:** `tests/integration/`
- **Scope:** Test module interactions
- **Database:** Use test database, not production

### End-to-End Tests
- **Location:** `tests/e2e/`
- **Scope:** Test complete user workflows
- **Data:** Use test fixtures

### Test Execution
- **Run Before Commit:** Run tests before committing code
- **CI/CD:** Run tests in CI/CD pipeline
- **Command:** `pytest tests/ --cov=src --cov-report=html`

---

## DOCUMENTATION STANDARDS

### Code Documentation
- **Docstrings:** All functions, classes, modules must have docstrings
- **Comments:** Explain WHY, not WHAT
- **README:** Keep README.md updated
- **API Docs:** Document all API endpoints

### Documentation Files
- **Location:** `docs/` directory
- **Format:** Markdown (.md) files
- **Sections:** Include overview, setup, usage, examples
- **Examples:** Include code examples

### Inline Comments
- **Purpose:** Explain complex logic
- **Style:** Clear, concise comments
- **Language:** English
- **Example:**
  ```python
  # Calculate risk-adjusted return using Sharpe ratio
  # Formula: (Return - Risk-free rate) / Standard deviation
  sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_std
  ```

---

## DATA HANDLING & PRIVACY

### Data Collection
- **Consent:** Always obtain user consent before collecting data
- **Minimal Data:** Collect only necessary data
- **Purpose:** Clearly state data collection purpose

### Data Storage
- **Encryption:** Encrypt sensitive data at rest
- **Access Control:** Implement access control for data
- **Retention:** Define data retention policies
- **Deletion:** Implement data deletion on user request

### GDPR Compliance
- **Right to Access:** Provide user data access
- **Right to Deletion:** Implement data deletion
- **Right to Portability:** Provide data export
- **Consent Management:** Track and manage user consent

### Financial Data
- **Sensitivity:** Financial data is highly sensitive
- **Access Logging:** Log all access to financial data
- **Encryption:** Use strong encryption (AES-256)
- **Backup:** Encrypt backups

---

## COMPLIANCE & REGULATORY

### Financial Regulations
- **SEC Compliance:** Follow SEC guidelines for financial advice
- **FINRA Compliance:** Follow FINRA suitability requirements
- **Disclaimers:** Include required disclaimers
- **Record Keeping:** Maintain required records

### Disclaimers
- **Required Text:** Include standard disclaimers:
  - "This is not financial advice"
  - "Past performance does not guarantee future results"
  - "Investments carry risk of loss"
- **Placement:** Display disclaimers prominently
- **Acknowledgment:** Require user acknowledgment

### Audit Trail
- **Logging:** Log all recommendations and user interactions
- **Retention:** Retain logs per regulatory requirements
- **Access:** Control access to audit logs

---

## PERFORMANCE STANDARDS

### Response Times
- **API Endpoints:** < 2 seconds for standard endpoints
- **LLM Responses:** < 10 seconds for generation
- **Database Queries:** < 500ms for standard queries
- **Page Load:** < 3 seconds for Streamlit pages

### Optimization
- **Caching:** Cache frequently accessed data
- **Database:** Optimize queries, use indexes
- **API Calls:** Minimize external API calls
- **Batch Processing:** Use batch operations when possible

### Resource Usage
- **Memory:** Monitor memory usage
- **CPU:** Optimize CPU-intensive operations
- **GPU:** Efficient GPU usage for model inference
- **Storage:** Manage storage efficiently

---

## CODE REVIEW CHECKLIST

### Before Submitting Code
- [ ] Code follows PEP 8 style guide
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] No hardcoded API keys or secrets
- [ ] Input validation implemented
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Tests written and passing
- [ ] Code coverage >= 80%
- [ ] No security vulnerabilities
- [ ] Documentation updated

### Security Checklist
- [ ] No API keys in code
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] Authentication implemented
- [ ] Authorization checked
- [ ] Sensitive data encrypted
- [ ] Error messages don't leak information

### Functionality Checklist
- [ ] Function works as expected
- [ ] Edge cases handled
- [ ] Error cases handled
- [ ] Performance acceptable
- [ ] Memory usage acceptable
- [ ] No memory leaks

---

## FRAMEWORK VERSION REQUIREMENTS

### Required Versions
```python
# Core
python>=3.9,<3.12
langchain>=0.1.0
openai>=1.0.0
streamlit>=1.28.0

# ML/AI
transformers>=4.35.0
torch>=2.1.0
sentence-transformers>=2.2.0
peft>=0.6.0

# Data
pandas>=2.0.0
numpy>=1.24.0
alpha-vantage>=2.3.0

# Database
psycopg2-binary>=2.9.0
sqlalchemy>=2.0.0

# Vector DB
pinecone-client>=2.0.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Version Pinning
- **Production:** Pin exact versions in `requirements.txt`
- **Development:** Use `>=` for development dependencies
- **Updates:** Test updates before deploying

---

## FILE ORGANIZATION RULES

### Directory Structure
```
project/
├── src/                    # Source code
│   ├── data_collection/    # Data collection modules
│   ├── model_training/     # Model training modules
│   ├── personalization/    # Personalization modules
│   ├── rag_pipeline/      # RAG pipeline modules
│   ├── compliance/         # Compliance modules
│   ├── api/               # API endpoints
│   └── utils/             # Utility modules
├── tests/                 # Test files
├── docs/                  # Documentation
├── config/                # Configuration files
├── data/                  # Data files
├── models/                 # Model files
└── ui/                    # UI components
```

### File Naming
- **Python Files:** `snake_case.py`
- **Test Files:** `test_<module_name>.py`
- **Config Files:** `kebab-case.yaml` or `snake_case.yaml`
- **Documentation:** `UPPER_SNAKE_CASE.md`

### Import Organization
- **Order:** Standard library → Third-party → Local
- **Grouping:** One blank line between groups
- **Absolute Imports:** Prefer absolute imports

---

## COMMIT MESSAGE STANDARDS

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

### Examples
```
feat(data_collection): Add Alpha Vantage API client with rate limiting

- Implement rate limiting (5 calls/min)
- Add error handling and retry logic
- Add caching support

Closes #123
```

---

## FINAL CHECKLIST BEFORE COMPLETION

### Code Quality
- [ ] All code follows style guide
- [ ] All functions have type hints and docstrings
- [ ] Code is well-organized and modular
- [ ] No code duplication
- [ ] Performance optimized

### Security
- [ ] No secrets in code
- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] Authentication/authorization implemented
- [ ] Data encryption implemented
- [ ] Error handling doesn't leak information

### Testing
- [ ] Unit tests written (>80% coverage)
- [ ] Integration tests written
- [ ] End-to-end tests written
- [ ] All tests passing

### Documentation
- [ ] README.md complete
- [ ] API documentation complete
- [ ] Code docstrings complete
- [ ] User guide complete
- [ ] Deployment guide complete

### Functionality
- [ ] All features implemented
- [ ] All requirements met
- [ ] Error handling comprehensive
- [ ] Performance acceptable
- [ ] User experience polished

### Compliance
- [ ] Disclaimers included
- [ ] GDPR compliance implemented
- [ ] SEC/FINRA guidelines followed
- [ ] Audit logging implemented
- [ ] Data retention policies implemented

---

## ENFORCEMENT

### Pre-commit Hooks
- Install pre-commit hooks to enforce style
- Run linters before commit
- Run tests before commit

### Code Review
- All code must be reviewed before merge
- Reviewers check against this rules file
- Address all review comments

### Continuous Integration
- Run tests in CI/CD pipeline
- Check code coverage
- Run security scans
- Validate code style

---

**Remember:** These rules exist to ensure code quality, security, and maintainability. Follow them strictly to deliver a production-ready system.

**Questions?** Refer to `PROJECT_DOCUMENTATION.md` for detailed specifications.

---

*End of Rules Document*

