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

def test_shorten_with_custom_alias():
    response = client.post(
        "/shortner",
        json={"url": "https://example.com/custom", "custom_alias": "my-link"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == "my-link"
    assert data["url"] == "https://example.com/custom"

def test_custom_alias_reserved_word_rejected():
    response = client.post(
        "/shortner",
        json={"url": "https://example.com", "custom_alias": "login"}
    )
    assert response.status_code == 400
    assert "reserved" in response.json()["detail"].lower()

def test_custom_alias_duplicate_rejected():
    # First request succeeds
    client.post(
        "/shortner",
        json={"url": "https://example.com/first", "custom_alias": "taken-alias"}
    )
    # Second request with same alias fails
    response = client.post(
        "/shortner",
        json={"url": "https://example.com/second", "custom_alias": "taken-alias"}
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["detail"].lower()

def test_link_expiration():
    from datetime import datetime, timedelta
    # Create a URL that expires in the past
    expired_time = datetime.utcnow() - timedelta(days=1)
    response = client.post(
        "/shortner",
        json={
            "url": "https://example.com/expired",
            "expires_at": expired_time.isoformat()
        }
    )
    assert response.status_code == 200
    short_url = response.json()["short_url"]
    
    # Try to access expired link
    response = client.get(f"/{short_url}", follow_redirects=False)
    assert response.status_code == 200  # Returns JSON, not redirect
    data = response.json()
    assert "expired" in data["message"].lower()

def test_link_not_expired():
    from datetime import datetime, timedelta
    # Create a URL that expires in the future
    future_time = datetime.utcnow() + timedelta(days=30)
    response = client.post(
        "/shortner",
        json={
            "url": "https://example.com/valid",
            "expires_at": future_time.isoformat()
        }
    )
    assert response.status_code == 200
    short_url = response.json()["short_url"]
    
    # Should redirect successfully
    response = client.get(f"/{short_url}", follow_redirects=False)
    assert response.status_code == 302

def test_enhanced_analytics_tracking():
    # Create URL
    res = client.post("/shortner", json={"url": "https://example.com/analytics"})
    short_url = res.json()["short_url"]
    
    # Visit URL with custom headers
    response = client.get(
        f"/{short_url}",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0",
            "Referer": "https://google.com"
        },
        follow_redirects=False
    )
    assert response.status_code == 302
    
    # Check analytics
    analytics_response = client.get(f"/analytics/{short_url}")
    assert analytics_response.status_code == 200
    analytics = analytics_response.json()
    assert len(analytics) > 0
    # First click should have browser/os/referrer data
    assert analytics[0]["browser"] is not None or analytics[0]["os"] is not None

def test_analytics_summary():
    # Create URL and generate some clicks
    res = client.post("/shortner", json={"url": "https://example.com/summary"})
    short_url = res.json()["short_url"]
    
    # Generate 5 clicks
    for _ in range(5):
        client.get(f"/{short_url}", follow_redirects=False)
    
    # Get summary
    response = client.get(f"/analytics/{short_url}/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_clicks"] == 5
    assert len(data["recent_clicks"]) == 5

def test_qr_code_generation():
    # Create URL
    response = client.post("/shortner", json={"url": "https://example.com/qr"})
    assert response.status_code == 200
    data = response.json()
    short_url = data["short_url"]
    assert data["qr_code_path"] is not None
    
    # Get QR code
    qr_response = client.get(f"/qr/{short_url}")
    assert qr_response.status_code == 200
    assert qr_response.headers["content-type"] == "image/png"

def test_search_urls():
    # Create multiple URLs
    client.post("/shortner", json={"url": "https://google.com/test"})
    client.post("/shortner", json={"url": "https://facebook.com/page"})
    client.post("/shortner", json={"url": "https://twitter.com/user"})
    
    # Search for "google"
    response = client.get("/testuser@example.com/get_all_urls?search=google")
    assert response.status_code == 200
    data = response.json()
    # Should find at least one result containing "google"
    assert len(data) >= 1
    urls = [item["url"] for item in data.values()]
    assert any("google" in url for url in urls)

def test_filter_by_clicks():
    # Create URLs with different click counts
    res1 = client.post("/shortner", json={"url": "https://example.com/popular"})
    short1 = res1.json()["short_url"]
    
    res2 = client.post("/shortner", json={"url": "https://example.com/unpopular"})
    short2 = res2.json()["short_url"]
    
    # Generate 10 clicks on first URL
    for _ in range(10):
        client.get(f"/{short1}", follow_redirects=False)
    
    # Filter by min_clicks=5
    response = client.get("/testuser@example.com/get_all_urls?min_clicks=5")
    assert response.status_code == 200
    data = response.json()
    # Should only return URLs with >= 5 clicks
    for item in data.values():
        assert item["clicks"] >= 5

def test_filter_by_expiration():
    from datetime import datetime, timedelta
    
    # Create expired URL
    expired_time = datetime.utcnow() - timedelta(days=1)
    client.post(
        "/shortner",
        json={"url": "https://example.com/old", "expires_at": expired_time.isoformat()}
    )
    
    # Create active URL
    future_time = datetime.utcnow() + timedelta(days=30)
    client.post(
        "/shortner",
        json={"url": "https://example.com/new", "expires_at": future_time.isoformat()}
    )
    
    # Filter for expired links
    response = client.get("/testuser@example.com/get_all_urls?expired=true")
    assert response.status_code == 200
    expired_urls = response.json()
    
    # Filter for active links
    response = client.get("/testuser@example.com/get_all_urls?expired=false")
    assert response.status_code == 200
    active_urls = response.json()
    
    # Should have both types
    assert len(expired_urls) >= 1
    assert len(active_urls) >= 1

def test_create_api_key():
    response = client.post(
        "/api-keys/",
        json={"name": "Test API Key"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test API Key"
    assert data["key"].startswith("sk_")
    assert data["is_active"] == True

def test_list_api_keys():
    # Create a couple of API keys
    client.post("/api-keys/", json={"name": "Key 1"})
    client.post("/api-keys/", json={"name": "Key 2"})
    
    # List all keys
    response = client.get("/api-keys/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_revoke_api_key():
    # Create API key
    res = client.post("/api-keys/", json={"name": "To Revoke"})
    key_id = res.json()["id"]
    
    # Revoke it
    response = client.delete(f"/api-keys/{key_id}")
    assert response.status_code == 200
    
    # Verify it's revoked
    response = client.get("/api-keys/")
    keys = response.json()
    revoked_key = next((k for k in keys if k["id"] == key_id), None)
    assert revoked_key is not None
    assert revoked_key["is_active"] == False

def test_api_key_authentication():
    # Create API key
    res = client.post("/api-keys/", json={"name": "Auth Test"})
    api_key = res.json()["key"]
    
    # Verify API key
    response = client.get(
        "/api-keys/verify",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] == True
    assert data["user_id"] == 1

def test_invalid_api_key():
    response = client.get(
        "/api-keys/verify",
        headers={"X-API-Key": "invalid_key_12345"}
    )
    assert response.status_code == 401

def test_filter_by_date_range():
    from datetime import datetime, timedelta
    
    # Create URLs at different times (we'll use created_at from database)
    client.post("/shortner", json={"url": "https://example.com/date1"})
    
    # Filter by created_after (should find recent URLs)
    yesterday = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = client.get(f"/testuser@example.com/get_all_urls?created_after={yesterday}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
