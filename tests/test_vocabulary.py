# tests/test_vocabulary.py
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from database import crud
from schemas.user import UserCreate
from schemas.vocabulary_item import VocabularyItemCreate

@pytest.mark.asyncio
async def test_create_vocabulary_item_authenticated(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "vocab_user",
        "email": "vocab@example.com",
        "password": "password123"
    })
    login_response = await async_client.post("/api/auth/token", data={
        "username": "vocab_user",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    response = await async_client.post(
        "/api/vocabulary/vocabulary-items",
        json={"russian_word": "привет", "translation": "hello", "example_sentence": "Привет, как дела?"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["russian_word"] == "привет"

@pytest.mark.asyncio
async def test_get_all_vocabulary_items(async_client: AsyncClient, db_session: Session):
    user = crud.create_user(db_session, UserCreate(username="vocab_getter", email="getter@test.com", password="pwd"), "hashed_pwd")
    crud.create_vocabulary_item(db_session, VocabularyItemCreate(russian_word="книга", translation="book"), user_id=user.id)
    response = await async_client.get("/api/vocabulary/vocabulary-items")
    assert response.status_code == 200
    assert len(response.json()) >= 1