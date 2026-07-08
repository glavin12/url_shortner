# ?? SnapLink — URL Shortener

> A production-grade URL shortening platform with analytics, QR codes, IP intelligence, and API key authentication.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green?style=flat-square&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?style=flat-square&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7-red?style=flat-square&logo=redis)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square&logo=docker)
![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen?style=flat-square)

---

## ?? What is SnapLink?

**SnapLink** is a full-stack URL shortener that goes beyond just making links shorter. It tells you **who clicked your link, from where, on what device, and how many times** — all in real time. You can even see **whose IP** is hitting your links.

Key highlights:
- ?? **JWT + API Key dual authentication**
- ?? **Per-click analytics** — browser, OS, referrer tracking
- ?? **IP tracking** — know exactly whose IP is hitting your links
- ? **Link expiration** — auto-expire links after a set time
- ?? **QR Code generation** — instant QR on every short link
- ?? **Search & filter** — find links by date, click count, expiry
- ?? **Docker-ready** — one command deployment
- ? **Redis caching** — blazing fast redirects

---

## ?? Architecture

```
Client Request
     ¦
     ?
FastAPI App (Rate Limited via SlowAPI)
     ¦
     +--? Redis Cache (fast lookup)
     ¦         ¦ Cache Miss
     ¦         ?
     +--? PostgreSQL DB
     ¦
     +--? Background Task (analytics: IP, browser, OS, referrer)
```

**Tech Stack:**

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.13) |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Auth | JWT + API Keys (`sk_` prefixed) |
| Containerization | Docker + Docker Compose |
| Frontend | React + Vite |
| Hosting | Railway (backend) · Vercel (frontend) |

---

## ? Features

### ?? URL Shortening
- Shorten any URL to a clean slug (e.g., `snaplink.io/abc123`)
- **Custom alias** support (e.g., `snaplink.io/my-brand`)
- Reserved alias protection (prevents conflicts)
- Duplicate URL detection

### ?? Analytics & IP Intelligence
- Tracks every click with:
  - **IP Address** of the visitor (know whose IP that is!)
  - **Browser** (Chrome, Firefox, Safari, etc.)
  - **OS** (Windows, macOS, Android, etc.)
  - **Referrer** (where the click came from)
  - **Timestamp** (UTC)
- Analytics summary endpoint with aggregated stats
- Pagination for large click datasets

### ?? QR Code Generation
- Auto-generated QR code on every URL creation
- Served as PNG via dedicated endpoint
- Stored persistently on disk

### ? Link Expiration
- Set an optional `expires_at` datetime on any link
- Expired links return a friendly JSON message
- Filter your dashboard by expiration status

### ?? API Key Authentication
- Generate `sk_`-prefixed API keys
- Use `X-API-Key` header as an alternative to JWT
- Track `last_used_at` per key
- Revoke keys at any time

### ? Performance
- Redis caching for O(1) redirect lookups
- Background task analytics (non-blocking)
- SQLAlchemy connection pooling
- Rate limiting on all endpoints

---

## ?? Getting Started

### Prerequisites
- Python 3.13+
- PostgreSQL 15+
- Redis 7+
- Docker (optional but recommended)

### ?? Docker (Recommended)

```bash
# Clone the repo
git clone https://github.com/yourusername/url_shortner.git
cd url_shortner

# Start all services
docker-compose up --build
```

Access the API at `http://localhost:8000`

### Manual Setup

```bash
# Install dependencies
cd backend_4
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL, REDIS_URL, SECRET_KEY

# Run the server
uvicorn main:app --reload
```

---

## ?? Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost/db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing secret | `your-super-secret-key` |
| `FRONTEND_URLS` | Allowed CORS origins | `https://yourdomain.com` |

---

## ??? API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login & get JWT token |

### URLs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/shorten` | Create a short URL |
| GET | `/{short_url}` | Redirect to original URL |
| GET | `/urls/` | List all your URLs (with search/filter) |
| DELETE | `/urls/{id}` | Delete a URL |
| GET | `/analytics/{short_url}` | Click analytics (with IP info) |
| GET | `/analytics/{short_url}/summary` | Aggregated analytics |
| GET | `/qr/{short_url}` | Get QR code image |

### API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api-keys/` | Create API key |
| GET | `/api-keys/` | List your API keys |
| DELETE | `/api-keys/{id}` | Revoke API key |
| GET | `/api-keys/verify` | Verify an API key |

---

## ?? Testing

```bash
cd backend_4
pytest tests/ -v
```

**Results: 25/25 tests passing ?**

```
test_shorten_url                        PASSED
test_shorten_duplicate_url              PASSED
test_get_short_url_redirect             PASSED
test_link_expiration                    PASSED
test_enhanced_analytics_tracking        PASSED
test_qr_code_generation                 PASSED
test_search_urls                        PASSED
test_create_api_key                     PASSED
test_api_key_authentication             PASSED
... (25 total)
```

---

## ?? Security

- **Bcrypt** password hashing
- **JWT** with expiration
- **API Keys** with `sk_` prefix (crypto-secure via `secrets` module)
- **Rate limiting** on all endpoints (SlowAPI)
- **SQLAlchemy ORM** prevents SQL injection
- **Pydantic** input validation

---

## ?? Deployment

Live at:
- **Backend**: [Railway](https://pretty-laughter-production.up.railway.app)
- **Frontend**: [Vercel](https://snaplink-iota.vercel.app)

---

## ?? Project Structure

```
url_shortner/
+-- backend_4/
¦   +-- main.py                 # FastAPI app entrypoint
¦   +-- database/
¦   ¦   +-- database.py         # SQLAlchemy engine & session
¦   ¦   +-- database_models.py  # ORM models
¦   ¦   +-- schemas.py          # Pydantic schemas
¦   +-- routes/
¦   ¦   +-- url_shortner.py     # Core URL endpoints
¦   ¦   +-- auth_route.py       # Auth endpoints
¦   ¦   +-- apikey_route.py     # API key endpoints
¦   +-- auth/                   # JWT utilities
¦   +-- limiter.py              # Rate limiter config
¦   +-- tests/                  # 25 test cases
¦   +-- Dockerfile
¦   +-- requirements.txt
+-- frontend_4/                 # React + Vite frontend
+-- docker-compose.yml
+-- README.md
```

---

## ?? Additional Docs

- [API Examples](./API_EXAMPLES.md) — cURL examples for every endpoint
- [Docker Guide](./DOCKER_GUIDE.md) — Docker setup & troubleshooting
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) — Technical deep dive

---

*Built with ?? using FastAPI, PostgreSQL, Redis & React*
