# tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

@pytest.fixture(autouse=True, scope="session")
def set_mock_llm_env():
    os.environ["LLM_PROVIDER"] = "mock"

@pytest.fixture
def client():
    return TestClient(app)
