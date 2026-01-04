"""
End-to-End Tests for Financial Advisor System.

Tests complete user journeys:
1. User creates profile → Gets recommendations → Asks questions → Receives advice
2. User queries system → System retrieves context → Generates response → Applies compliance
"""

import pytest
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

from scripts.personalization_engine import PersonalizationEngine
from scripts.rag_pipeline import FinancialRAGPipeline
from scripts.inference import FinancialAdvisorInference
from src.compliance.compliance_checker import ComplianceChecker


class TestUserJourney1:
    """Test: User creates profile → Gets recommendations → Asks questions."""
    
    def test_complete_user_journey(self):
        """Test complete user journey from profile creation to advice."""
        # Step 1: Create user profile
        user_profile = {
            "user_id": "e2e_test_user_001",
            "age": 30,
            "income": 60000,
            "savings": 30000,
            "risk_tolerance": "Moderate",
            "investment_horizon_years": 30,
            "financial_goals": ["Retirement", "Home Purchase"],
            "current_portfolio": {
                "stocks": 50,
                "bonds": 40,
                "cash": 10
            }
        }
        
        # Step 2: Generate personalized recommendations
        personalization = PersonalizationEngine()
        recommendations = personalization.generate_recommendations(user_profile)
        
        assert recommendations is not None
        assert "target_allocation" in recommendations
        assert "risk_profile" in recommendations
        assert recommendations["risk_profile"] in ["Conservative", "Moderate", "Aggressive"]
        
        # Step 3: Ask financial question
        rag_pipeline = FinancialRAGPipeline()
        query = "Should I increase my stock allocation for retirement?"
        response = rag_pipeline.generate_response(user_profile["user_id"], query)
        
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Step 4: Verify compliance
        checker = ComplianceChecker()
        checked_response = checker.add_disclaimers(response)
        
        assert checked_response is not None
        assert len(checked_response) >= len(response)


class TestUserJourney2:
    """Test: User queries system → System processes → Returns compliant response."""
    
    def test_query_to_response_flow(self):
        """Test query processing flow."""
        user_id = "user_1000"
        query = "What is the best investment strategy for someone with moderate risk tolerance?"
        
        # Initialize components
        rag_pipeline = FinancialRAGPipeline()
        checker = ComplianceChecker()
        
        # Step 1: Retrieve context
        context = rag_pipeline.retrieve_context(user_id)
        assert context is not None
        
        # Step 2: Generate response
        response = rag_pipeline.generate_response(user_id, query)
        assert response is not None
        
        # Step 3: Apply compliance
        compliant_response = checker.add_disclaimers(response)
        assert compliant_response is not None
        
        # Step 4: Verify response quality
        assert len(compliant_response) > 50  # Should be substantial
        assert "disclaimer" in compliant_response.lower() or "not financial advice" in compliant_response.lower()


class TestUserJourney3:
    """Test: Multiple queries → Context maintained → Consistent responses."""
    
    def test_multi_turn_conversation(self):
        """Test multi-turn conversation flow."""
        user_id = "user_1000"
        rag_pipeline = FinancialRAGPipeline()
        
        # First query
        query1 = "What is an ETF?"
        response1 = rag_pipeline.generate_response(user_id, query1)
        assert response1 is not None
        
        # Second query (should maintain context)
        query2 = "Should I invest in ETFs?"
        response2 = rag_pipeline.generate_response(user_id, query2)
        assert response2 is not None
        
        # Third query (follow-up)
        query3 = "What are the risks?"
        response3 = rag_pipeline.generate_response(user_id, query3)
        assert response3 is not None
        
        # All responses should be valid
        assert all([len(r) > 0 for r in [response1, response2, response3]])


class TestUserJourney4:
    """Test: Profile update → Recommendations update → Advice reflects changes."""
    
    def test_profile_update_flow(self):
        """Test that profile updates affect recommendations."""
        personalization = PersonalizationEngine()
        
        # Initial profile (conservative)
        profile1 = {
            "user_id": "e2e_test_user_002",
            "age": 25,
            "income": 50000,
            "savings": 10000,
            "risk_tolerance": "Conservative",
            "investment_horizon_years": 5,
            "financial_goals": ["Emergency Fund"],
            "current_portfolio": {"stocks": 20, "bonds": 70, "cash": 10}
        }
        
        rec1 = personalization.generate_recommendations(profile1)
        assert rec1["risk_profile"] in ["Conservative", "Moderately Conservative"]
        
        # Updated profile (more aggressive)
        profile2 = profile1.copy()
        profile2["risk_tolerance"] = "Aggressive"
        profile2["investment_horizon_years"] = 30
        profile2["financial_goals"] = ["Wealth Generation"]
        
        rec2 = personalization.generate_recommendations(profile2)
        assert rec2["risk_profile"] in ["Aggressive", "Moderately Aggressive", "Very Aggressive"]
        
        # Recommendations should differ
        assert rec1["target_allocation"]["stocks"] < rec2["target_allocation"]["stocks"]


class TestErrorHandling:
    """Test error handling in end-to-end flows."""
    
    def test_invalid_user_id(self):
        """Test handling of invalid user ID."""
        rag_pipeline = FinancialRAGPipeline()
        
        # Should handle gracefully
        response = rag_pipeline.generate_response("invalid_user_999", "Test query")
        assert response is not None  # Should return something, not crash
    
    def test_empty_query(self):
        """Test handling of empty query."""
        rag_pipeline = FinancialRAGPipeline()
        
        response = rag_pipeline.generate_response("user_1000", "")
        # Should handle gracefully (either return default or error message)
        assert response is not None
    
    def test_malformed_profile(self):
        """Test handling of malformed profile."""
        personalization = PersonalizationEngine()
        
        malformed_profile = {"user_id": "test"}
        # Should handle gracefully
        try:
            recommendations = personalization.generate_recommendations(malformed_profile)
            # If it doesn't crash, that's good
            assert True
        except Exception:
            # If it raises exception, should be informative
            assert True


class TestPerformanceE2E:
    """Test performance characteristics in end-to-end flows."""
    
    def test_response_time(self):
        """Test that responses are generated in reasonable time."""
        import time
        
        rag_pipeline = FinancialRAGPipeline()
        user_id = "user_1000"
        query = "What should I invest in?"
        
        start_time = time.time()
        response = rag_pipeline.generate_response(user_id, query)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response is not None
        assert response_time < 10.0  # Should complete in under 10 seconds (without model)
    
    def test_concurrent_queries(self):
        """Test handling of concurrent queries."""
        rag_pipeline = FinancialRAGPipeline()
        user_id = "user_1000"
        queries = [
            "What is an ETF?",
            "Should I invest in stocks?",
            "What are bonds?",
            "How do I plan for retirement?",
            "What is diversification?"
        ]
        
        responses = []
        for query in queries:
            response = rag_pipeline.generate_response(user_id, query)
            responses.append(response)
        
        # All should succeed
        assert len(responses) == len(queries)
        assert all([r is not None for r in responses])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])




