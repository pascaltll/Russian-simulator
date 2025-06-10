# tests/test_auth.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient):
    response = await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

@pytest.mark.asyncio
async def test_register_user_duplicate_username(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    })
    response = await async_client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "another@example.com",
        "password": "password123"
    })
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_for_access_token(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "password123"
    })
    response = await async_client.post("/api/auth/token", data={
        "username": "loginuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()