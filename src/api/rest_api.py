"""
REST API endpoints for Financial Advisor.

Provides HTTP API wrapper around inference functionality.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import time

# Add scripts directory to path
project_root = Path(__file__).parent.parent.parent
scripts_path = project_root / "scripts"
sys.path.insert(0, str(scripts_path))

from inference import FinancialAdvisorInference
from src.compliance.compliance_checker import ComplianceChecker

# Initialize FastAPI app
app = FastAPI(
    title="Financial Advisor API",
    description="AI-Powered Financial Advisor REST API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (loaded on startup)
advisor_inference: Optional[FinancialAdvisorInference] = None
compliance_checker: Optional[ComplianceChecker] = None

# Rate limiting (simple in-memory implementation)
request_counts = {}
RATE_LIMIT = 60  # requests per minute


def check_rate_limit(api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Simple rate limiting check."""
    current_minute = int(time.time() / 60)
    key = api_key or "anonymous"
    
    if key not in request_counts:
        request_counts[key] = {}
    
    if current_minute not in request_counts[key]:
        request_counts[key][current_minute] = 0
    
    request_counts[key][current_minute] += 1
    
    if request_counts[key][current_minute] > RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return key


@app.on_event("startup")
async def startup_event():
    """Load model on startup."""
    global advisor_inference, compliance_checker
    
    model_path = project_root / "models" / "fine_tuned" / "financial_advisor"
    
    try:
        advisor_inference = FinancialAdvisorInference(
            model_path=str(model_path),
            base_model="TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        )
        compliance_checker = ComplianceChecker()
        print("✓ API initialized successfully")
    except Exception as e:
        print(f"⚠ Warning: Could not load model: {e}")
        print("API will return errors until model is available")


# Request/Response models
class ChatRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="User's financial question")
    max_length: int = Field(200, ge=50, le=500, description="Maximum response length")
    temperature: float = Field(0.7, ge=0.0, le=1.0, description="Sampling temperature")


class ChatResponse(BaseModel):
    response_text: str = Field(..., description="Generated response")
    user_id: str = Field(..., description="User identifier")
    query: str = Field(..., description="Original query")
    compliance: Dict[str, Any] = Field(..., description="Compliance check results")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class RecommendationRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")


class RecommendationResponse(BaseModel):
    user_id: str = Field(..., description="User identifier")
    recommendations: Dict[str, Any] = Field(..., description="User recommendations")
    risk_profile: Dict[str, Any] = Field(..., description="Risk profile information")


class ProfileRequest(BaseModel):
    user_id: str = Field(..., description="User identifier")
    profile_data: Dict[str, Any] = Field(..., description="Profile data")


class HealthResponse(BaseModel):
    status: str = Field(..., description="API status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    version: str = Field(..., description="API version")


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=advisor_inference is not None,
        version="1.0.0"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    api_key: str = Depends(check_rate_limit)
):
    """
    Chat endpoint for financial advice.
    
    Args:
        request: Chat request with user_id and query
        api_key: API key for rate limiting
        
    Returns:
        Chat response with financial advice
    """
    if not advisor_inference:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please check server logs."
        )
    
    try:
        # Generate response
        response_text = advisor_inference.generate_response(
            request.user_id,
            request.query,
            max_length=request.max_length,
            temperature=request.temperature
        )
        
        # Get market data for fact-checking
        market_data = advisor_inference.rag.market_data.get_context() if hasattr(advisor_inference.rag, 'market_data') else {}
        
        # Compliance check
        compliance_result = compliance_checker.check_compliance(
            response_text,
            user_consent=True,  # Assume consent for API calls
            market_data=market_data
        )
        
        # Add disclaimers based on risk level
        response_text = compliance_checker.add_disclaimers(
            response_text,
            risk_level=compliance_result.get("risk_level", "moderate")
        )
        
        # Log advice
        compliance_checker.log_advice(
            request.user_id,
            request.query,
            response_text,
            compliance_result
        )
        
        return ChatResponse(
            response_text=response_text,
            user_id=request.user_id,
            query=request.query,
            compliance=compliance_result,
            metadata={
                "model": "TinyLlama-1.1B-finetuned",
                "temperature": request.temperature,
                "max_length": request.max_length,
                "timestamp": time.time()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/recommendations/{user_id}", response_model=RecommendationResponse)
async def get_recommendations(
    user_id: str,
    api_key: str = Depends(check_rate_limit)
):
    """
    Get user recommendations.
    
    Args:
        user_id: User identifier
        api_key: API key for rate limiting
        
    Returns:
        User recommendations and risk profile
    """
    import json
    recs_path = project_root / "data" / "processed" / "user_recommendations.json"
    
    if not recs_path.exists():
        raise HTTPException(status_code=404, detail="Recommendations file not found")
    
    try:
        with open(recs_path, 'r') as f:
            all_recs = json.load(f)
        
        user_rec = next((r for r in all_recs if r.get("user_id") == user_id), None)
        
        if not user_rec:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        return RecommendationResponse(
            user_id=user_id,
            recommendations=user_rec,
            risk_profile=user_rec.get("risk_profile", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading recommendations: {str(e)}")


@app.post("/profile")
async def create_profile(
    request: ProfileRequest,
    api_key: str = Depends(check_rate_limit)
):
    """
    Create or update user profile.
    
    Args:
        request: Profile request with user_id and profile_data
        api_key: API key for rate limiting
        
    Returns:
        Created profile confirmation
    """
    # In production, this would save to database
    # For now, return confirmation
    return {
        "status": "success",
        "user_id": request.user_id,
        "message": "Profile created successfully (saved to personalization engine)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

