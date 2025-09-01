"""
Unit tests for app.routers.health module.
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.routers.health import router


class TestHealthRouter:
    """Test the health router."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_health_endpoint(self):
        """Test the health endpoint."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_endpoint_method_not_allowed(self):
        """Test that only GET is allowed on health endpoint."""
        response = self.client.post("/health")
        assert response.status_code == 405  # Method Not Allowed
        
        response = self.client.put("/health")
        assert response.status_code == 405  # Method Not Allowed
        
        response = self.client.delete("/health")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_health_endpoint_content_type(self):
        """Test that health endpoint returns JSON."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
    
    def test_health_endpoint_response_structure(self):
        """Test that health endpoint response has correct structure."""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "status" in data
        assert data["status"] == "ok"
        assert len(data) == 1  # Only status field
    
    def test_health_endpoint_multiple_calls(self):
        """Test that health endpoint is consistent across multiple calls."""
        for _ in range(5):
            response = self.client.get("/health")
            
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
    
    def test_health_endpoint_with_query_params(self):
        """Test health endpoint with query parameters (should still work)."""
        response = self.client.get("/health?param=value")
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_endpoint_with_headers(self):
        """Test health endpoint with custom headers."""
        headers = {
            "User-Agent": "Test-Agent",
            "Custom-Header": "Test-Value"
        }
        
        response = self.client.get("/health", headers=headers)
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestHealthRouterAsync:
    """Test the health router with async client."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
    
    @pytest.mark.asyncio
    async def test_health_endpoint_async(self):
        """Test the health endpoint with async client."""
        from httpx import AsyncClient
        
        async with AsyncClient(app=self.app, base_url="http://test") as ac:
            response = await ac.get("/health")
            
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
    
    @pytest.mark.asyncio
    async def test_health_endpoint_concurrent_requests(self):
        """Test health endpoint with concurrent requests."""
        import asyncio
        from httpx import AsyncClient
        
        async def make_request(client):
            response = await client.get("/health")
            return response.status_code, response.json()
        
        async with AsyncClient(app=self.app, base_url="http://test") as ac:
            # Make 10 concurrent requests
            tasks = [make_request(ac) for _ in range(10)]
            results = await asyncio.gather(*tasks)
            
            # All requests should succeed
            for status_code, data in results:
                assert status_code == 200
                assert data == {"status": "ok"}


class TestHealthRouterTags:
    """Test health router tags and OpenAPI integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_openapi_schema_includes_health(self):
        """Test that health endpoint is included in OpenAPI schema."""
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        openapi_schema = response.json()
        
        # Check that /health path exists
        assert "/health" in openapi_schema["paths"]
        
        # Check that GET method exists for /health
        health_path = openapi_schema["paths"]["/health"]
        assert "get" in health_path
        
        # Check tags
        health_get = health_path["get"]
        assert "tags" in health_get
        assert "health" in health_get["tags"]
    
    def test_openapi_health_response_schema(self):
        """Test that health endpoint response schema is correct in OpenAPI."""
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        openapi_schema = response.json()
        
        health_get = openapi_schema["paths"]["/health"]["get"]
        
        # Check response structure
        assert "responses" in health_get
        assert "200" in health_get["responses"]
        
        response_200 = health_get["responses"]["200"]
        assert "description" in response_200
        assert "content" in response_200
        assert "application/json" in response_200["content"]


class TestHealthRouterEdgeCases:
    """Test edge cases for the health router."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
    
    def test_health_endpoint_case_sensitivity(self):
        """Test that health endpoint is case sensitive."""
        # Correct case should work
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # Different cases should not work
        response = self.client.get("/HEALTH")
        assert response.status_code == 404
        
        response = self.client.get("/Health")
        assert response.status_code == 404
    
    def test_health_endpoint_trailing_slash(self):
        """Test health endpoint with trailing slash."""
        # Without trailing slash (defined route)
        response = self.client.get("/health")
        assert response.status_code == 200
        
        # With trailing slash (should also work due to FastAPI's redirect)
        response = self.client.get("/health/", follow_redirects=True)
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_endpoint_with_body(self):
        """Test health endpoint with request body (should ignore it)."""
        response = self.client.get("/health", json={"test": "data"})
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_health_endpoint_response_time(self):
        """Test that health endpoint responds quickly."""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        assert response_time < 1.0  # Should respond in less than 1 second
