import pytest
from fastapi.testclient import TestClient
from src.api.server import app
import os

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def setup_data_dir():
    # Ensure data directory exists
    os.makedirs("./data/sessions", exist_ok=True)
    yield
    # Cleanup could go here, but for now we leave files for inspection if needed
