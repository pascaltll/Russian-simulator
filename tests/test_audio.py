# tests/test_audio.py
import pytest
from httpx import AsyncClient
import os
import io

@pytest.mark.asyncio
async def test_transcribe_audio_unauthenticated(async_client: AsyncClient):
    with open("tests/dummy.wav", "wb") as f:
        f.write(b"dummy audio data")
    response = await async_client.post(
        "/api/audio/transcribe-audio",
        files={"audio_file": ("dummy.wav", open("tests/dummy.wav", "rb"), "audio/wav")}
    )
    assert response.status_code == 401
    os.remove("tests/dummy.wav")

@pytest.mark.asyncio
async def test_transcribe_audio_authenticated(async_client: AsyncClient):
    await async_client.post("/api/auth/register", json={
        "username": "audio_user",
        "email": "audio@example.com",
        "password": "password123"
    })
    login_response = await async_client.post("/api/auth/token", data={
        "username": "audio_user",
        "password": "password123"
    })
    token = login_response.json()["access_token"]
    
    with open("tests/dummy.wav", "wb") as f:
        f.write(b"dummy audio data")
    with open("tests/dummy.wav", "rb") as f:
        response = await async_client.post(
            "/api/audio/transcribe-audio",
            files={"audio_file": ("dummy.wav", f, "audio/wav")},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 201
    os.remove("tests/dummy.wav")