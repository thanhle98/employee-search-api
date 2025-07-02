import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time
from src.main import app, rate_limiter
from src.middleware.rate_limit import RATE_LIMIT_REQUESTS

client = TestClient(app)

class TestRateLimit:
    """Test suite for rate limiting functionality"""
    
    def setup_method(self):
        """Reset rate limiter state before each test"""
        rate_limiter.request_history.clear()
        rate_limiter.last_cleanup = time.time()
  
    def test_different_ips_have_separate_limits(self):
        """Test that different IP addresses have separate rate limits"""
        endpoint = "/api/v1/employees/search"
        
        # Mock different client IPs
        with patch.object(rate_limiter, '_get_client_ip') as mock_get_ip:
            # First IP makes requests up to limit
            mock_get_ip.return_value = "192.168.1.1"
            for i in range(RATE_LIMIT_REQUESTS):
                response = client.get(endpoint)
                assert response.status_code == 200
            
            # First IP should now be rate limited
            response = client.get(endpoint)
            assert response.status_code == 429
            
            # Second IP should still be able to make requests
            mock_get_ip.return_value = "192.168.1.2"
            response = client.get(endpoint)
            assert response.status_code == 200
    
  
    def test_concurrent_requests_from_same_ip(self):
        """Test that concurrent requests from same IP are properly rate limited"""
        endpoint = "/api/v1/employees/search"
        
        # Simulate rapid requests by making many requests quickly
        responses = []
        for i in range(RATE_LIMIT_REQUESTS + 5):
            response = client.get(endpoint)
            responses.append(response)
        
        # Count successful vs rate limited responses
        successful = [r for r in responses if r.status_code == 200]
        rate_limited = [r for r in responses if r.status_code == 429]
        
        # Should have exactly RATE_LIMIT_REQUESTS successful requests
        assert len(successful) == RATE_LIMIT_REQUESTS
        # Rest should be rate limited
        assert len(rate_limited) == 5
        
        # Verify last response is rate limited
        assert responses[-1].status_code == 429 