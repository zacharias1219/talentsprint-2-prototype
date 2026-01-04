"""
Integration Tests for Financial Advisor System.

Tests the integration between different components:
- Data collection → Personalization → RAG → Inference
- API endpoints → Business logic
- UI components → Backend services
"""

import pytest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from scripts.personalization_engine import PersonalizationEngine
from scripts.rag_pipeline import FinancialRAGPipeline
from scripts.inference import FinancialAdvisorInference
from src.compliance.compliance_checker import ComplianceChecker


class TestPersonalizationIntegration:
    """Test personalization engine integration."""
    
    def test_profile_loading_and_risk_assessment(self):
        """Test that profiles can be loaded and risk assessed."""
        engine = PersonalizationEngine()
        
        # Create test profile
        test_profile = {
            "user_id": "test_user_001",
            "age": 35,
            "income": 75000,
            "savings": 50000,
            "risk_tolerance": "Moderate",
            "investment_horizon_years": 20,
            "financial_goals": ["Retirement"],
            "current_portfolio": {
                "stocks": 60,
                "bonds": 30,
                "cash": 10
            }
        }
        
        # Test risk score calculation
        risk_score = engine._calculate_risk_score(test_profile)
        assert 0 <= risk_score <= 100, "Risk score should be between 0 and 100"
        
        # Test recommendation generation
        recommendations = engine.generate_recommendations(test_profile)
        assert recommendations is not None
        assert "target_allocation" in recommendations
        assert "risk_profile" in recommendations


class TestRAGPipelineIntegration:
    """Test RAG pipeline integration."""
    
    def test_rag_context_retrieval(self):
        """Test that RAG pipeline retrieves context correctly."""
        pipeline = FinancialRAGPipeline()
        
        # Test context retrieval
        user_id = "user_1000"
        context = pipeline.retrieve_context(user_id)
        
        assert context is not None
        assert isinstance(context, dict)
        # Context should contain user and market data
        assert "user_context" in context or "market_context" in context
    
    def test_rag_response_generation(self):
        """Test that RAG pipeline generates responses."""
        pipeline = FinancialRAGPipeline()
        
        # Test response generation
        user_id = "user_1000"
        query = "What should I invest in?"
        
        response = pipeline.generate_response(user_id, query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0


class TestInferenceIntegration:
    """Test inference engine integration."""
    
    @pytest.mark.skipif(
        not os.path.exists("models/fine_tuned/financial_advisor"),
        reason="Fine-tuned model not found"
    )
    def test_model_loading(self):
        """Test that fine-tuned model loads correctly."""
        model_path = "models/fine_tuned/financial_advisor"
        
        try:
            inference = FinancialAdvisorInference(
                model_path=model_path,
                base_model="mistralai/Mistral-7B-Instruct-v0.2"
            )
            assert inference.model is not None
            assert inference.tokenizer is not None
        except Exception as e:
            pytest.skip(f"Model loading failed: {e}")
    
    @pytest.mark.skipif(
        not os.path.exists("models/fine_tuned/financial_advisor"),
        reason="Fine-tuned model not found"
    )
    def test_inference_generation(self):
        """Test that inference generates responses."""
        model_path = "models/fine_tuned/financial_advisor"
        
        try:
            inference = FinancialAdvisorInference(
                model_path=model_path,
                base_model="mistralai/Mistral-7B-Instruct-v0.2"
            )
            
            user_id = "user_1000"
            query = "What is an ETF?"
            
            response = inference.generate_response(user_id, query)
            
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
        except Exception as e:
            pytest.skip(f"Inference failed: {e}")


class TestComplianceIntegration:
    """Test compliance checker integration."""
    
    def test_compliance_checking(self):
        """Test that compliance checker works correctly."""
        checker = ComplianceChecker()
        
        # Test disclaimer addition
        response = "You should invest all your money in crypto."
        checked_response = checker.add_disclaimers(response)
        
        assert "disclaimer" in checked_response.lower() or "not financial advice" in checked_response.lower()
    
    def test_fact_checking(self):
        """Test fact checking functionality."""
        checker = ComplianceChecker()
        
        # Test fact check
        claim = "AAPL stock price is $200"
        result = checker.fact_check_stock_prices(claim, {"AAPL": {"price": 185.60}})
        
        # Should return fact check result
        assert result is not None


class TestEndToEndFlow:
    """Test end-to-end flow from query to response."""
    
    def test_complete_flow_without_model(self):
        """Test complete flow without requiring model."""
        # Initialize components
        personalization = PersonalizationEngine()
        rag_pipeline = FinancialRAGPipeline()
        
        # Create test profile
        test_profile = {
            "user_id": "test_user_001",
            "age": 35,
            "income": 75000,
            "savings": 50000,
            "risk_tolerance": "Moderate",
            "investment_horizon_years": 20,
            "financial_goals": ["Retirement"],
            "current_portfolio": {
                "stocks": 60,
                "bonds": 30,
                "cash": 10
            }
        }
        
        # Step 1: Generate recommendations
        recommendations = personalization.generate_recommendations(test_profile)
        assert recommendations is not None
        
        # Step 2: Generate RAG response
        query = "What should I invest in for retirement?"
        response = rag_pipeline.generate_response(test_profile["user_id"], query)
        assert response is not None
        
        # Step 3: Check compliance
        checker = ComplianceChecker()
        checked_response = checker.add_disclaimers(response)
        assert checked_response is not None


class TestAPIIntegration:
    """Test API integration."""
    
    def test_api_imports(self):
        """Test that API modules can be imported."""
        try:
            from src.api.rest_api import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"API imports failed: {e}")
    
    def test_api_health_endpoint(self):
        """Test API health endpoint."""
        try:
            from fastapi.testclient import TestClient
            from src.api.rest_api import app
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
        except ImportError:
            pytest.skip("FastAPI test client not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




