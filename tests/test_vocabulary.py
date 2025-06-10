# tests/test_vocabulary.py
import pytest

# ... (código existente para test_create_vocabulary_item, test_get_vocabulary_items, test_delete_vocabulary_item) ...

def test_suggest_translation(client, auth_headers):
    payload = {
        "russian_word": "молоко",
        "target_language": "en"
    }

    response = client.post(
        "/api/vocabulary/suggest-translation",
        json=payload,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    # ¡CORREGIDO AQUÍ! Cambiado de "translation" a "suggested_translation"
    assert "suggested_translation" in data
    assert "suggested_example_sentence" in data # Asegurarse de que esta también se verifica

    # Si sabes qué traducción y ejemplo esperas, puedes ser más específico:
    # assert data["suggested_translation"] == "Leche"
    # assert data["suggested_example_sentence"] == "Ejemplo: 'Leche'."