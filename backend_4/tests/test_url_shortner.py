import sys
from unittest.mock import MagicMock

# 1. Mock Redis before importing anything else to prevent network connection attempts
mock_redis = MagicMock()
mock_redis.get.return_value = None
mock_redis.set.return_value = True
mock_redis.delete.return_value = True

class MockRedisModule:
    r = mock_redis

sys.modules['database.redis_1'] = MockRedisModule

import database
database.redis_1 = MockRedisModule

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.database import Base, get_db
from database.database_models import UrlShortner, clickanalytic, users
from auth.auth_jwt import verify_access_token
from limiter import limiter
from main import app

# Disable rate limiter for testing
limiter.enabled = False

import os
# Setup test SQLite database (file-based to preserve connection across threads/tasks)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
if os.path.exists("./test.db"):
    try:
        os.remove("./test.db")
    except Exception:
        pass

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency override
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Auth dependency override (acting as testuser@example.com with user_id=1)
def override_verify_access_token():
    return {
        "sub": "testuser@example.com",
        "user_id": 1,
        "type": "ACCESS"
    }

# Apply overrides
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_access_token] = override_verify_access_token

# Override SessionLocal inside url_shortner routes so background tasks (e.g. record_click) use test database
import routes.url_shortner
routes.url_shortner.SessionLocal = TestingSessionLocal

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Re-create tables before each test to ensure test isolation
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Seed a test user (since user_id=1 is referenced by mock auth)
    db = TestingSessionLocal()
    test_user = users(user_id=1, email="testuser@example.com", password="hashed_password")
    db.add(test_user)
    db.commit()
    db.close()
    yield
    
    # Clean up test.db after test completes
    if os.path.exists("./test.db"):
        try:
            os.remove("./test.db")
        except Exception:
            pass

def test_shorten_url():
    response = client.post(
        "/shortner",
        json={"url": "https://example.com/very/long/url/path"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com/very/long/url/path"
    assert "short_url" in data
    assert len(data["short_url"]) == 6

def test_shorten_duplicate_url():
    # Shorten once
    client.post("/shortner", json={"url": "https://example.com"})
    # Shorten same URL again (should return the existing one)
    response = client.post("/shortner", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"

def test_get_short_url_redirect():
    # Create short URL
    res_short = client.post("/shortner", json={"url": "https://google.com"})
    short_url = res_short.json()["short_url"]
    
    # Try resolving (Redirects to target url with status code 302)
    response = client.get(f"/{short_url}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://google.com"

def test_get_short_url_not_found():
    response = client.get("/nonexistent")
    assert response.status_code == 200  # Returns JSON message on not found
    assert response.json() == {"message": "url not found"}

def test_get_all_urls_paginated():
    # Insert multiple URLs (15 URLs)
    for i in range(15):
        client.post("/shortner", json={"url": f"https://example.com/{i}"})
        
    # Get page 1 (size = 10)
    response = client.get("/testuser@example.com/get_all_urls?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    
    # Get page 2 (size = 10)
    response = client.get("/testuser@example.com/get_all_urls?page=2&size=10")
    assert response.status_code == 200
    data_page_2 = response.json()
    assert len(data_page_2) == 5

def test_get_analytics_paginated():
    # Create short URL
    res_short = client.post("/shortner", json={"url": "https://google.com"})
    short_url = res_short.json()["short_url"]
    
    # Record clicks (12 clicks)
    for _ in range(12):
        client.get(f"/{short_url}", follow_redirects=False)
        
    # Fetch paginated analytics (page 1, size 10)
    response = client.get(f"/analytics/{short_url}?page=1&size=10")
    assert response.status_code == 200
    analytics = response.json()
    assert len(analytics) == 10
    
    # Fetch paginated analytics (page 2, size 10)
    response = client.get(f"/analytics/{short_url}?page=2&size=10")
    assert response.status_code == 200
    analytics_page_2 = response.json()
    assert len(analytics_page_2) == 2

def test_delete_url():
    # Create short URL
    res_short = client.post("/shortner", json={"url": "https://yahoo.com"})
    short_url = res_short.json()["short_url"]
    
    # Delete URL
    response = client.delete(f"/delete/{short_url}")
    assert response.status_code == 200
    assert response.json() == "https://yahoo.com"
    
    # Verify it's gone
    response = client.get(f"/{short_url}")
    assert response.json() == {"message": "url not found"}

def test_delete_all_urls():
    # Create a couple of short URLs
    client.post("/shortner", json={"url": "https://example.com/1"})
    client.post("/shortner", json={"url": "https://example.com/2"})
    
    # Delete all URLs
    response = client.delete("/testuser@example.com/delete_all_urls")
    assert response.status_code == 200
    assert response.json() == {"message": "all urls deleted successfully"}
    
    # Verify list is empty
    response = client.get("/testuser@example.com/get_all_urls")
    assert response.json() == {}
