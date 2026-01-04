# Financial Advisor API Documentation

## Overview

The Financial Advisor REST API provides programmatic access to the AI-powered financial advisory system. It wraps the inference functionality and provides structured JSON responses with compliance checks.

## Base URL

```
http://localhost:8000
```

## Authentication

API uses API key-based rate limiting. Include your API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/chat
```

**Rate Limits:** 60 requests per minute per API key.

## Endpoints

### 1. Health Check

**GET** `/health`

Check API status and model availability.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### 2. Chat Endpoint

**POST** `/chat`

Generate financial advice based on user query.

**Request Body:**
```json
{
  "user_id": "user_1000",
  "query": "Should I invest in ETFs this year?",
  "max_length": 200,
  "temperature": 0.7
}
```

**Parameters:**
- `user_id` (required): User identifier
- `query` (required): Financial question
- `max_length` (optional): Maximum response length (50-500, default: 200)
- `temperature` (optional): Sampling temperature (0.0-1.0, default: 0.7)

**Response:**
```json
{
  "response_text": "Based on your Moderately Aggressive risk profile...",
  "user_id": "user_1000",
  "query": "Should I invest in ETFs this year?",
  "compliance": {
    "compliant": true,
    "warnings": [],
    "risk_level": "moderate",
    "disclaimers_added": true,
    "fact_check": {
      "checked": true,
      "symbols_found": ["VTI"],
      "errors": [],
      "compliant": true
    }
  },
  "metadata": {
    "model": "gpt2-finetuned",
    "temperature": 0.7,
    "max_length": 200,
    "timestamp": 1703456789.123
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "user_id": "user_1000",
    "query": "What do you think about Apple stock?"
  }'
```

---

### 3. Get Recommendations

**GET** `/recommendations/{user_id}`

Retrieve user's financial recommendations and risk profile.

**Path Parameters:**
- `user_id`: User identifier

**Response:**
```json
{
  "user_id": "user_1000",
  "recommendations": {
    "risk_profile": {
      "score": 75,
      "label": "Moderately Aggressive"
    },
    "target_allocation": {
      "stocks": 80,
      "bonds": 15,
      "cash": 5
    },
    "action_plan": [
      "Increase Stock allocation by 71% to boost growth.",
      "Deploy 24% cash into markets."
    ]
  },
  "risk_profile": {
    "score": 75,
    "label": "Moderately Aggressive"
  }
}
```

**Example:**
```bash
curl http://localhost:8000/recommendations/user_1000 \
  -H "X-API-Key: your-api-key"
```

---

### 4. Create Profile

**POST** `/profile`

Create or update user profile.

**Request Body:**
```json
{
  "user_id": "user_1000",
  "profile_data": {
    "age": 35,
    "income": 100000,
    "risk_tolerance": "High",
    "financial_goals": ["Retirement"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "user_id": "user_1000",
  "message": "Profile created successfully"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "User user_1234 not found"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error generating response: Model not loaded"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Model not loaded. Please check server logs."
}
```

## Compliance & Disclaimers

All responses include:
- Automatic compliance checking
- Fact-checking against market data
- Risk-level warnings for high-risk recommendations
- Regulatory disclaimers
- Audit logging

## Usage Examples

### Python
```python
import requests

api_key = "your-api-key"
base_url = "http://localhost:8000"

# Chat endpoint
response = requests.post(
    f"{base_url}/chat",
    headers={"X-API-Key": api_key},
    json={
        "user_id": "user_1000",
        "query": "Should I invest in mutual funds?"
    }
)

print(response.json()["response_text"])
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

const apiKey = 'your-api-key';
const baseUrl = 'http://localhost:8000';

axios.post(`${baseUrl}/chat`, {
  user_id: 'user_1000',
  query: 'What is your opinion on tech stocks?'
}, {
  headers: {
    'X-API-Key': apiKey
  }
})
.then(response => {
  console.log(response.data.response_text);
});
```

## Deployment

### Running the API Server

```bash
# Using uvicorn directly
python -m uvicorn src.api.rest_api:app --host 0.0.0.0 --port 8000

# Or using the script
python src/api/rest_api.py
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "uvicorn", "src.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Monitoring

- All API calls are logged with duration and status codes
- Model inference times are tracked
- API key usage is monitored for rate limiting
- Advice is logged for audit trail in `logs/advice_audit/`

## Version

Current API version: **1.0.0**
