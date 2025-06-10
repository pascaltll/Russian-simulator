"""
Module for testing authentication API endpoints.

These tests cover user registration and login functionalities,
including scenarios for duplicate usernames and successful token retrieval.
"""
# Group 1: Standard libraries
# No standard library imports needed here.

# Group 2: Third-party libraries
import pytest
from httpx import AsyncClient # Corrected import order (C0411)


@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    """
    Test successful user registration.

    Ensures that a new user can be registered successfully with a 201 status code
    and that the returned data contains the correct username.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making requests.
    """
    response = await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_register_user_duplicate_username(async_client: AsyncClient):
    """
    Test registration attempt with a duplicate username.

    Ensures that registering a user with an already existing username results
    in a 400 Bad Request status code and an appropriate error message.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making requests.
    """
    # Register the first user
    await async_client.post("/api/auth/register", json={
        "username": "testuser_duplicate", # Changed username to avoid conflict with other tests
        "email": "test@example.com",
        "password": "password123"
    })
    # Attempt to register with the same username
    response = await async_client.post("/api/auth/register", json={
        "username": "testuser_duplicate",
        "email": "another@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient):
    """
    Test successful user login and access token retrieval.

    Ensures that a registered user can log in and receive an access token
    with a 200 OK status code.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making requests.
    """
    # Register a user for login testing
    await async_client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123"
    })
    # Attempt to log in
    response = await async_client.post("/api/auth/token", data={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
