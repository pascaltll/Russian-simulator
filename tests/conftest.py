# tests/conftest.py

import os
import sys # <-- Añadir esta importación

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from main import app
from database.base_class import Base
from database.config import get_db

# DB de test
TEST_DATABASE_URL = "sqlite:///./tests/test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None)

@pytest_asyncio.fixture(name="async_client")
async def async_client_fixture(db_session: Session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture(name="auth_headers")
async def auth_headers_fixture(async_client: AsyncClient):
    """
    Registers a user and logs them in, returning authorization headers.
    """
    # Register a user
    username = "test_user"
    email = "test@example.com"
    password = "testpassword"

    await async_client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    # Log in to get a token
    login_response = await async_client.post("/api/auth/token", data={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}