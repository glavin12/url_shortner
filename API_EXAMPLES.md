# API Examples - FastAPI URL Shortener

Complete examples for all API endpoints with request/response samples.

## Authentication

### Register User

**Request:**
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Login

**Request:**
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Refresh Token

**Request:**
```bash
curl -X POST "http://localhost:8000/refresh_token" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer REFRESH_TOKEN"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## URL Shortening

### Create Short URL (Simple)

**Request:**
```bash
curl -X POST "http://localhost:8000/shortner" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "url": "https://www.example.com/very/long/url/path"
  }'
```

**Response:**
```json
{
  "id": 1,
  "url": "https://www.example.com/very/long/url/path",
  "short_url": "P2ztAE",
  "clicks": 0,
  "created_at": "2024-06-20T10:30:00",
  "expires_at": null,
  "qr_code_path": "backend_4/qr_codes/qr_1_P2ztAE.png",
  "user_id": 1
}
```

### Create Short URL with Custom Alias

**Request:**
```bash
curl -X POST "http://localhost:8000/shortner" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "url": "https://www.example.com",
    "custom_alias": "my-custom-link"
  }'
```

**Response:**
```json
{
  "id": 2,
  "url": "https://www.example.com",
  "short_url": "my-custom-link",
  "clicks": 0,
  "created_at": "2024-06-20T10:31:00",
  "expires_at": null,
  "qr_code_path": "backend_4/qr_codes/qr_2_my-custom-link.png",
  "user_id": 1
}
```

### Create Short URL with Expiration

**Request:**
```bash
curl -X POST "http://localhost:8000/shortner" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "url": "https://www.example.com/limited-offer",
    "custom_alias": "summer-sale",
    "expires_at": "2024-12-31T23:59:59"
  }'
```

**Response:**
```json
{
  "id": 3,
  "url": "https://www.example.com/limited-offer",
  "short_url": "summer-sale",
  "clicks": 0,
  "created_at": "2024-06-20T10:32:00",
  "expires_at": "2024-12-31T23:59:59",
  "qr_code_path": "backend_4/qr_codes/qr_3_summer-sale.png",
  "user_id": 1
}
```

### Access Short URL (Redirect)

**Request:**
```bash
curl -L "http://localhost:8000/P2ztAE"
```

**Response:**
HTTP 302 redirect to the original URL

### Access Expired Link

**Request:**
```bash
curl "http://localhost:8000/expired-link"
```

**Response:**
```json
{
  "message": "This link has expired",
  "expired_at": "2024-06-19T23:59:59"
}
```

---

## URL Management

### Get All User URLs

**Request:**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?page=1&size=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "1": {
    "url": "https://www.example.com/very/long/url/path",
    "short_url": "P2ztAE",
    "clicks": 5,
    "created_at": "2024-06-20T10:30:00",
    "expires_at": null,
    "qr_code_path": "backend_4/qr_codes/qr_1_P2ztAE.png"
  },
  "2": {
    "url": "https://www.example.com",
    "short_url": "my-custom-link",
    "clicks": 12,
    "created_at": "2024-06-20T10:31:00",
    "expires_at": null,
    "qr_code_path": "backend_4/qr_codes/qr_2_my-custom-link.png"
  }
}
```

### Search URLs

**Request:**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?search=example" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Filter URLs by Clicks

**Request:**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?min_clicks=10&max_clicks=100" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Filter URLs by Date

**Request:**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?created_after=2024-06-01T00:00:00" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Filter by Expiration Status

**Request (Only Expired):**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?expired=true" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Request (Only Active):**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?expired=false" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Combined Filters

**Request:**
```bash
curl "http://localhost:8000/john@example.com/get_all_urls?search=sale&min_clicks=5&expired=false&page=1&size=20" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

### Delete Specific URL

**Request:**
```bash
curl -X DELETE "http://localhost:8000/delete/P2ztAE" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
"https://www.example.com/very/long/url/path"
```

### Delete All URLs

**Request:**
```bash
curl -X DELETE "http://localhost:8000/john@example.com/delete_all_urls" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "all urls deleted successfully"
}
```

---

## Analytics

### Get Click Analytics (Paginated)

**Request:**
```bash
curl "http://localhost:8000/analytics/P2ztAE?page=1&size=10" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "url_id": 1,
    "clicked_at": "2024-06-20T11:00:00",
    "browser": "Chrome 91.0",
    "os": "Windows 10",
    "referrer": "https://google.com"
  },
  {
    "id": 2,
    "url_id": 1,
    "clicked_at": "2024-06-20T11:05:00",
    "browser": "Firefox 89.0",
    "os": "macOS 11.0",
    "referrer": "https://twitter.com"
  }
]
```

### Get Analytics Summary

**Request:**
```bash
curl "http://localhost:8000/analytics/P2ztAE/summary" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "total_clicks": 15,
  "recent_clicks": [
    {
      "id": 15,
      "url_id": 1,
      "clicked_at": "2024-06-20T12:00:00",
      "browser": "Safari 14.1",
      "os": "iOS 14.6",
      "referrer": "https://facebook.com"
    },
    {
      "id": 14,
      "url_id": 1,
      "clicked_at": "2024-06-20T11:58:00",
      "browser": "Chrome 91.0",
      "os": "Android 11",
      "referrer": null
    }
  ]
}
```

---

## QR Codes

### Get QR Code

**Request:**
```bash
curl "http://localhost:8000/qr/P2ztAE" --output qr.png
```

**Response:**
Binary PNG image

**HTML Example:**
```html
<img src="http://localhost:8000/qr/P2ztAE" alt="QR Code">
```

---

## API Key Management

### Create API Key

**Request:**
```bash
curl -X POST "http://localhost:8000/api-keys/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -d '{
    "name": "Production Server Key"
  }'
```

**Response:**
```json
{
  "id": 1,
  "key": "sk_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn",
  "name": "Production Server Key",
  "created_at": "2024-06-20T10:00:00",
  "last_used_at": null,
  "is_active": true
}
```

### List API Keys

**Request:**
```bash
curl "http://localhost:8000/api-keys/" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "key": "sk_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn",
    "name": "Production Server Key",
    "created_at": "2024-06-20T10:00:00",
    "last_used_at": "2024-06-20T11:30:00",
    "is_active": true
  },
  {
    "id": 2,
    "key": "sk_XYZABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij",
    "name": "Development Key",
    "created_at": "2024-06-20T10:05:00",
    "last_used_at": null,
    "is_active": true
  }
]
```

### Verify API Key

**Request:**
```bash
curl "http://localhost:8000/api-keys/verify" \
  -H "X-API-Key: sk_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn"
```

**Response:**
```json
{
  "valid": true,
  "user_id": 1
}
```

### Revoke API Key

**Request:**
```bash
curl -X DELETE "http://localhost:8000/api-keys/1" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Response:**
```json
{
  "message": "API key revoked successfully"
}
```

### Use API Key for Authentication

**Example: Create Short URL with API Key**
```bash
curl -X POST "http://localhost:8000/shortner" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmn" \
  -d '{
    "url": "https://www.example.com"
  }'
```

**Note:** API key authentication can be used as an alternative to JWT tokens for most endpoints.

---

## Error Responses

### Invalid Credentials

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```
Status: 401 Unauthorized

### Reserved Alias

**Response:**
```json
{
  "detail": "'login' is a reserved word and cannot be used as a custom alias"
}
```
Status: 400 Bad Request

### Duplicate Alias

**Response:**
```json
{
  "detail": "The alias 'my-link' is already taken. Please choose a different one."
}
```
Status: 409 Conflict

### URL Not Found

**Response:**
```json
{
  "message": "url not found"
}
```
Status: 200 OK (returns JSON instead of redirect)

### Rate Limit Exceeded

**Response:**
```json
{
  "detail": "Rate limit exceeded: 5 per 1 minute"
}
```
Status: 429 Too Many Requests

---

## Python Examples

### Using Requests Library

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/register",
    json={
        "name": "John Doe",
        "email": "john@example.com",
        "password": "securepass123"
    }
)
print(response.json())

# Login
response = requests.post(
    f"{BASE_URL}/login",
    json={
        "email": "john@example.com",
        "password": "securepass123"
    }
)
tokens = response.json()
access_token = tokens["access_token"]

# Create short URL
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(
    f"{BASE_URL}/shortner",
    json={
        "url": "https://www.example.com",
        "custom_alias": "my-link",
        "expires_at": "2024-12-31T23:59:59"
    },
    headers=headers
)
short_url_data = response.json()
print(f"Short URL: {BASE_URL}/{short_url_data['short_url']}")

# Get analytics
response = requests.get(
    f"{BASE_URL}/analytics/{short_url_data['short_url']}/summary",
    headers=headers
)
analytics = response.json()
print(f"Total clicks: {analytics['total_clicks']}")

# Download QR code
response = requests.get(f"{BASE_URL}/qr/{short_url_data['short_url']}")
with open("qr_code.png", "wb") as f:
    f.write(response.content)
```

### Using HTTPX (Async)

```python
import asyncio
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Register
        response = await client.post(
            "http://localhost:8000/register",
            json={
                "name": "John Doe",
                "email": "john@example.com",
                "password": "securepass123"
            }
        )
        
        # Login
        response = await client.post(
            "http://localhost:8000/login",
            json={
                "email": "john@example.com",
                "password": "securepass123"
            }
        )
        tokens = response.json()
        
        # Create short URL
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.post(
            "http://localhost:8000/shortner",
            json={"url": "https://www.example.com"},
            headers=headers
        )
        print(response.json())

asyncio.run(main())
```

---

## JavaScript Examples

### Using Fetch API

```javascript
const BASE_URL = 'http://localhost:8000';

// Register
const registerResponse = await fetch(`${BASE_URL}/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'John Doe',
    email: 'john@example.com',
    password: 'securepass123'
  })
});

// Login
const loginResponse = await fetch(`${BASE_URL}/login`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'john@example.com',
    password: 'securepass123'
  })
});
const { access_token } = await loginResponse.json();

// Create short URL
const shortUrlResponse = await fetch(`${BASE_URL}/shortner`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    url: 'https://www.example.com',
    custom_alias: 'my-link'
  })
});
const shortUrlData = await shortUrlResponse.json();
console.log(`Short URL: ${BASE_URL}/${shortUrlData.short_url}`);

// Get analytics summary
const analyticsResponse = await fetch(
  `${BASE_URL}/analytics/${shortUrlData.short_url}/summary`,
  {
    headers: { 'Authorization': `Bearer ${access_token}` }
  }
);
const analytics = await analyticsResponse.json();
console.log('Total clicks:', analytics.total_clicks);
```

---

## Postman Collection

Import this JSON into Postman for a complete collection:

```json
{
  "info": {
    "name": "URL Shortener API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    },
    {
      "key": "access_token",
      "value": ""
    }
  ],
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/register",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"name\": \"John Doe\",\n  \"email\": \"john@example.com\",\n  \"password\": \"securepass123\"\n}"
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/login",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"john@example.com\",\n  \"password\": \"securepass123\"\n}"
            }
          }
        }
      ]
    }
  ]
}
```

---

For more information, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
