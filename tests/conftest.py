# tests/conftest.py

import os
import sys
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

import warnings
# Las siguientes líneas ignoran advertencias específicas para mantener la salida de Pytest limpia.
# La advertencia de Whisper (FP16 en CPU) ya se abordó en utils/whisper_transcriber.py,
# pero la dejamos aquí comentada como referencia si necesitaras suprimirla de nuevo.
# warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead", category=UserWarning)
# Esta supresión de advertencia para httpx es para el caso donde el mensaje persiste
# a pesar de usar la sintaxis correcta.
warnings.filterwarnings("ignore", message="The 'app' shortcut is now deprecated. Use the explicit style 'transport=ASGITransport(app=...)' instead.", category=DeprecationWarning)


from main import app
from database.base_class import Base
from database.config import get_db

# Configuración de la base de datos de prueba
TEST_DATABASE_URL = "sqlite:///./tests/test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """
    Fixture para configurar y limpiar la base de datos de prueba.
    Crea todas las tablas antes de los tests y las elimina después.
    """
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    """
    Fixture para proporcionar una sesión de base de datos aislada para cada test.
    Cada test se ejecuta en una transacción que se revierte al finalizar,
    asegurando un estado limpio para el siguiente test.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback() # Revierte la transacción para limpiar la base de datos
        connection.close()

@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """
    Fixture para un cliente de prueba síncrono de FastAPI.
    Sobrescribe la dependencia de la base de datos para usar la sesión de prueba.
    """
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    # TestClient no usa el argumento 'transport' de la misma manera que AsyncClient
    with TestClient(app=app) as test_client:
        yield test_client
    app.dependency_overrides.pop(get_db, None) # Limpia la sobrescritura

@pytest_asyncio.fixture(name="async_client")
async def async_client_fixture(db_session: Session):
    """
    Fixture para un cliente de prueba asíncrono de FastAPI.
    Sobrescribe la dependencia de la base de datos para usar la sesión de prueba.
    Utiliza el estilo explícito de 'transport' para httpx.AsyncClient.
    """
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    # ¡CORRECCIÓN CRÍTICA AQUÍ! Eliminar el 'app=app' directo
    # Ahora solo se pasa 'app' dentro del 'transport' para cumplir con las últimas versiones de httpx.
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as ac:
        yield ac
    app.dependency_overrides.pop(get_db, None) # Limpia la sobrescritura


@pytest_asyncio.fixture(name="auth_headers")
async def auth_headers_fixture(async_client: AsyncClient):
    """
    Fixture para registrar un usuario y obtener sus encabezados de autorización.
    Esto permite que los tests autenticados puedan realizar solicitudes.
    """
    # Registra un usuario de prueba
    username = "test_user"
    email = "test@example.com"
    password = "testpassword"

    await async_client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password
    })

    # Inicia sesión para obtener un token de acceso
    login_response = await async_client.post("/api/auth/token", data={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    # Devuelve los encabezados de autorización en el formato esperado
    return {"Authorization": f"Bearer {token}"}
