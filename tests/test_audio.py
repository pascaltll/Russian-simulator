"""
Module for testing the audio transcription API endpoints.

These tests cover both authenticated and unauthenticated scenarios for
audio transcription and ensure correct response structures.
"""
# Group 1: Standard libraries
import os

# Group 2: Third-party libraries
import pytest
from httpx import AsyncClient  # Corrected import order (C0411)

AUDIO_FILE_PATH = "tests/audio/test_audio_1.ogg"

@pytest.mark.asyncio
async def test_transcribe_audio_authenticated(async_client: AsyncClient, auth_headers: dict):
    """
    Test authenticated audio transcription using an existing audio file.

    Ensures that a logged-in user can successfully submit an audio file
    for transcription and receives a valid transcription result.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making requests.
        auth_headers (dict): Authentication headers for the authenticated user.
    """
    if not os.path.exists(AUDIO_FILE_PATH):
        pytest.fail(f"Audio file not found at specified path: {AUDIO_FILE_PATH}")

    media_type = "audio/ogg"

    with open(AUDIO_FILE_PATH, "rb") as audio_file:
        files = {"audio_file": (os.path.basename(AUDIO_FILE_PATH), audio_file, media_type)}
        response = await async_client.post(
            "/api/audio/transcribe-audio",
            headers=auth_headers,
            files=files
        )

    assert response.status_code == 201

    # --- CORRECTION HERE! Changed 'transcribed_text' to 'original_transcript' ---
    # Break long line to avoid line-too-long (C0301)
    json_response = response.json()
    assert "original_transcript" in json_response
    assert isinstance(json_response["original_transcript"], str)

    # W1203: Use lazy % formatting in logging functions - Not applicable to print, but for consistency.
    print(f"Transcribed Text: {json_response['original_transcript']}")


@pytest.mark.asyncio
async def test_transcribe_audio_unauthenticated(async_client: AsyncClient):
    """
    Test unauthenticated audio transcription (should return 401 Unauthorized).

    Ensures that attempts to transcribe audio without proper authentication
    are rejected with a 401 status code.

    Args:
        async_client (AsyncClient): Asynchronous HTTP client for making requests.
    """
    if not os.path.exists(AUDIO_FILE_PATH):
        pytest.fail(f"Audio file not found at specified path: {AUDIO_FILE_PATH}")

    media_type = "audio/ogg"

    with open(AUDIO_FILE_PATH, "rb") as audio_file:
        files = {"audio_file": (os.path.basename(AUDIO_FILE_PATH), audio_file, media_type)}
        response = await async_client.post(
            "/api/audio/transcribe-audio",
            files=files
        )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"
