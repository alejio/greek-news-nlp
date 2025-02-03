"""Tests for the main FastAPI application.

This module contains tests for the FastAPI application endpoints and middleware.
It uses pytest-asyncio for testing async endpoints and httpx for making HTTP requests.
"""
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client fixture for synchronous tests.
    
    Returns:
        TestClient: A TestClient instance for testing the API.
    """
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client fixture for async tests.
    
    Yields:
        AsyncClient: An AsyncClient instance for testing the API.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_root_endpoint_async(async_client: AsyncClient) -> None:
    """Test the root endpoint returns correct API information using async client.
    
    Args:
        async_client: The async test client fixture.
    """
    response = await async_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Greek News NLP API",
        "version": "0.1.0",
        "status": "active"
    }


def test_root_endpoint_sync(client: TestClient) -> None:
    """Test the root endpoint returns correct API information using sync client.
    
    Args:
        client: The sync test client fixture.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "name": "Greek News NLP API",
        "version": "0.1.0",
        "status": "active"
    }


def test_cors_preflight(client: TestClient) -> None:
    """Test that CORS preflight requests are handled correctly.
    
    Args:
        client: The test client fixture.
    """
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_root_endpoint_method_not_allowed(client: TestClient, method: str) -> None:
    """Test that non-GET methods to root endpoint return 405 Method Not Allowed.
    
    Args:
        client: The test client fixture.
        method: The HTTP method to test.
    """
    response = client.request(method, "/")
    assert response.status_code == 405
