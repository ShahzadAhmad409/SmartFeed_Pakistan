import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import engine, Base
import os

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
