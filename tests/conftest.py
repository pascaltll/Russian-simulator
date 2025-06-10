"""
Pytest configuration and fixtures for the FastAPI application tests.

This module sets up a test database, provides isolated database sessions
for each test, and configures synchronous and asynchronous test clients
with overridden database dependencies. It also includes a fixture for
authenticated headers.
"""
# Group 1: Standard libraries
import warnings

# Group 2: Third-party libraries
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Group 3: First-party modules (C0413: Corrected import position)
from main import app
from database.base_class import Base
from database.config import get_db

warnings.filterwarnings( # C0301: Line too long - split for readability (already done)
    "ignore",
    message=(
        "The 'app' shortcut is now deprecated. Use the explicit style "
        "'transport=ASGITransport(app=...)' instead."
    ),
    category=DeprecationWarning
)

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./tests/test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Fixture to set up and tear down the test database.
    It creates all tables before the tests and drops them afterwards.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Fixture to provide an isolated database session for each test.
    Each test runs within a transaction that is rolled back upon completion,
    ensuring a clean state for the next test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback() # Rolls back the transaction to clean the database
        connection.close()

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """
    Fixture for a synchronous FastAPI test client.
    It overrides the database dependency to use the test session.
    """
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    # TestClient does not use the 'transport' argument in the same way as AsyncClient
    with TestClient(app=app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None) # Cleans up the override

@pytest_asyncio.fixture(name="async_client")
async def async_client_fixture(db_session: Session):
    """
    Fixture for an asynchronous FastAPI test client.
    It overrides the database dependency to use the test session.
    Uses the explicit 'transport' style for httpx.AsyncClient.
    """
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    # C0301: Line too long (117/100) - Corrected by splitting the line
    async with AsyncClient(
        base_url="http://test", transport=ASGITransport(app=app)
    ) as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None) # Cleans up the override


@pytest_asyncio.fixture(name="auth_headers")
async def auth_headers_fixture(async_client: AsyncClient):
    """
    Fixture to register a user and obtain their authorization headers.
    This allows authenticated tests to make requests.
    """
    # Register a test user
    username = "test_user"
    email = "test@example.com"
    password = "testpassword"

    await async_client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    # Log in to get an access token
    # C0301: Line too long (178/100) - Corrected by splitting the line
    login_response = await async_client.post(
        "/api/auth/token",
        data={
            "username": username,
            "password": password
        }
    )
    token = login_response.json()["access_token"]
    # Returns the authorization headers in the expected format
    return {"Authorization": f"Bearer {token}"}
