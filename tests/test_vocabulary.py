"""
Module for testing vocabulary API endpoints.

These tests cover creating, retrieving, deleting vocabulary items,
and also testing the translation suggestion functionality.
"""
# Group 1: Standard libraries
# No standard library imports needed here.

# Group 2: Third-party libraries
import pytest
from httpx import AsyncClient # Corrected import order (C0411)

# Group 3: First-party modules
# No first-party imports needed here for tests, as FastAPI client mocks them.


# Placeholder for existing tests, if not provided.
# If you have actual implementations for these tests, replace these placeholders.

@pytest.mark.asyncio
async def test_create_vocabulary_item(async_client: AsyncClient, auth_headers: dict):
    """
    Test creation of a new vocabulary item.

    Ensures that an authenticated user can successfully add a new vocabulary item
    to their list.
    """
    payload = {
        "russian_word": "привет",
        "translation": "hello",
        "example_sentence": "Привет, как дела?"
    }
    response = await async_client.post(
        "/api/vocabulary/",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["russian_word"] == "привет"
    assert response.json()["translation"] == "hello"


@pytest.mark.asyncio
async def test_get_vocabulary_items(async_client: AsyncClient, auth_headers: dict):
    """
    Test retrieving all vocabulary items for the current user.

    Ensures that an authenticated user can fetch their list of vocabulary items.
    """
    # Create a vocabulary item first to ensure there's something to retrieve
    await async_client.post(
        "/api/vocabulary/",
        json={"russian_word": "да", "translation": "yes"},
        headers=auth_headers
    )
    response = await async_client.get(
        "/api/vocabulary/",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["russian_word"] == "да"


@pytest.mark.asyncio
async def test_delete_vocabulary_item(async_client: AsyncClient, auth_headers: dict):
    """
    Test deleting a vocabulary item by ID.

    Ensures that an authenticated user can delete their own vocabulary items.
    """
    # Create an item to be deleted
    create_response = await async_client.post(
        "/api/vocabulary/",
        json={"russian_word": "нет", "translation": "no"},
        headers=auth_headers
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    # Delete the item
    delete_response = await async_client.delete(
        f"/api/vocabulary/{item_id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204 # No Content on successful deletion

    # Try to retrieve it to confirm deletion
    get_response = await async_client.get(
        "/api/vocabulary/",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    assert not any(item["id"] == item_id for item in get_response.json())


@pytest.mark.asyncio
async def test_suggest_translation(async_client: AsyncClient, auth_headers: dict):
    """
    Test the vocabulary translation suggestion endpoint.

    Ensures that the NLP service can suggest a translation and example
    sentence for a given Russian word.
    """
    payload = {
        "russian_word": "молоко",
        "target_language": "en"
    }

    response = await async_client.post(
        "/api/vocabulary/suggest-translation",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # CORRECTED HERE! Changed from "translation" to "suggested_translation"
    assert "suggested_translation" in data
    assert "suggested_example_sentence" in data # Ensure this is also checked

    # If you know what translation and example to expect, you can be more specific:
    # assert data["suggested_translation"] == "Milk" # Example for English
    # assert data["suggested_example_sentence"].startswith("Example: 'Milk'.") # Example for English
