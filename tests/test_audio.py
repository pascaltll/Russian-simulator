# tests/test_audio.py
import pytest
from httpx import AsyncClient
import os

AUDIO_FILE_PATH = "tests/audio/test_audio_1.ogg"

@pytest.mark.asyncio
async def test_transcribe_audio_authenticated(async_client: AsyncClient, auth_headers: dict):
    """
    Test authenticated audio transcription using an existing audio file.
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

    # --- ¡CORREGIDO AQUÍ! Cambiando 'transcribed_text' a 'original_transcript' ---
    assert "original_transcript" in response.json()
    assert isinstance(response.json()["original_transcript"], str)

    print(f"Transcribed Text: {response.json()['original_transcript']}")

@pytest.mark.asyncio
async def test_transcribe_audio_unauthenticated(async_client: AsyncClient):
    """
    Test unauthenticated audio transcription (should return 401).
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