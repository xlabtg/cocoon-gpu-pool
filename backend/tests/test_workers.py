"""Tests for worker endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_list_workers():
    """Test listing workers."""
    response = client.get("/api/v1/workers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_worker():
    """Test creating a worker."""
    # First create a participant
    participant_data = {
        "ton_wallet_address": "UQTest123",
        "username": "testuser"
    }
    participant_response = client.post("/api/v1/participants", json=participant_data)
    assert participant_response.status_code == 200
    participant_id = participant_response.json()["id"]

    # Create worker
    worker_data = {
        "participant_id": participant_id,
        "worker_name": "Test-Worker",
        "instance_number": 0,
        "host": "localhost",
        "stats_port": 12000,
        "price_coefficient": 1.0
    }
    response = client.post("/api/v1/workers", json=worker_data)
    assert response.status_code == 200
    assert response.json()["worker_name"] == "Test-Worker"


def test_get_worker():
    """Test getting a specific worker."""
    # Create test data first
    participant_data = {
        "ton_wallet_address": "UQTest456",
        "username": "testuser2"
    }
    participant_response = client.post("/api/v1/participants", json=participant_data)
    participant_id = participant_response.json()["id"]

    worker_data = {
        "participant_id": participant_id,
        "worker_name": "Test-Worker-2",
        "instance_number": 1,
        "host": "localhost",
        "stats_port": 12010
    }
    create_response = client.post("/api/v1/workers", json=worker_data)
    worker_id = create_response.json()["id"]

    # Get worker
    response = client.get(f"/api/v1/workers/{worker_id}")
    assert response.status_code == 200
    assert response.json()["id"] == worker_id


def test_update_worker():
    """Test updating a worker."""
    # Create test data
    participant_data = {
        "ton_wallet_address": "UQTest789",
        "username": "testuser3"
    }
    participant_response = client.post("/api/v1/participants", json=participant_data)
    participant_id = participant_response.json()["id"]

    worker_data = {
        "participant_id": participant_id,
        "worker_name": "Test-Worker-3",
        "instance_number": 2,
        "host": "localhost",
        "stats_port": 12020
    }
    create_response = client.post("/api/v1/workers", json=worker_data)
    worker_id = create_response.json()["id"]

    # Update worker
    update_data = {"is_active": False}
    response = client.patch(f"/api/v1/workers/{worker_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_get_nonexistent_worker():
    """Test getting a worker that doesn't exist."""
    response = client.get("/api/v1/workers/99999")
    assert response.status_code == 404
