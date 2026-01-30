import pytest

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "AI Dungeon Master is online"}

def test_start_session(client):
    response = client.post("/session/start", json={"campaign_type": "dark fantasy"})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "intro_narrative" in data
    assert "party_state" in data
    assert data["session_id"].startswith("sess_")
    return data["session_id"]

def test_interact(client):
    # First start a session to get a valid ID
    session_id = test_start_session(client)

    response = client.post("/interact", json={
        "user_id": "user_123",
        "character_id": "char_123",
        "input_text": "I attack the goblin",
        "session_id": session_id
    })

    assert response.status_code == 200
    data = response.json()
    assert "narrative" in data
    assert "audio_cues" in data
    assert "visual_cue" in data
    assert "state_update" in data
    # The simulated response includes "goblin shrieks"
    assert "goblin" in data["narrative"].lower()

def test_interact_invalid_session(client):
    response = client.post("/interact", json={
        "user_id": "user_123",
        "character_id": "char_123",
        "input_text": "hello",
        "session_id": "sess_invalid_999"
    })

    assert response.status_code == 200
    # Should still work because we have a fallback mock, but let's check logs if we could
    # For now just ensuring it doesn't crash
