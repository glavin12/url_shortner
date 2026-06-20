# FastAPI URL Shortener - Production-Ready

A feature-rich, production-oriented URL shortener built with FastAPI, PostgreSQL, Redis, and comprehensive analytics.

## 🚀 Features

### Core Features
- **URL Shortening** with automatic random IDs or custom aliases
- **JWT Authentication** for secure user management
- **Rate Limiting** to prevent abuse
- **Redis Caching** for high-performance redirects
- **PostgreSQL Database** for reliable data persistence

### New Features (2024 Upgrade)

#### 1. Custom Alias Support ✅
- Users can specify custom aliases for short URLs
- Global uniqueness enforcement
- Reserved words protection (login, register, admin, docs, etc.)
- Validation: 3-30 characters, alphanumeric + hyphens/underscores

```json
POST /shortner
{
  "url": "https://example.com",
  "custom_alias": "my-link"
}
```

#### 2. Link Expiration ⏰
- Optional expiration date for short URLs
- Automatic expiration checking on redirect
- Meaningful error messages for expired links
- Filter URLs by expiration status

```json
POST /shortner
{
  "url": "https://example.com",
  "expires_at": "2024-12-31T23:59:59"
}
```

#### 3. Enhanced Analytics 📊
- **Track:**
  - Total clicks
  - Click timestamp
  - Browser (Chrome, Firefox, Safari, etc.)
  - Operating System (Windows, macOS, Linux, etc.)
  - Referrer URL
- Paginated analytics endpoints
- Summary endpoint with recent clicks

```
GET /analytics/{short_url}
GET /analytics/{short_url}/summary
```

#### 4. QR Code Generation 📱
- Automatic QR code generation for each shortened URL
- QR codes stored as PNG images
- Dedicated endpoint to retrieve QR codes

```
GET /qr/{short_url}
```

#### 5. Search and Filtering 🔍
- **Search** by URL or short URL
- **Filter** by:
  - Click count range (min_clicks, max_clicks)
  - Creation date range (created_after, created_before)
  - Expiration status (expired=true/false)
- Pagination support

```
GET /{user_email}/get_all_urls?search=example&min_clicks=10&expired=false
```

#### 6. API Key Authentication 🔑
- Generate multiple API keys per user
- Authenticate using `X-API-Key` header
- Track API key usage (last_used_at)
- Revoke/deactivate keys

```
POST /api-keys/          # Create new API key
GET /api-keys/           # List all keys
DELETE /api-keys/{id}    # Revoke key
GET /api-keys/verify     # Verify key validity
```

#### 7. Docker Support 🐳
- Multi-stage Dockerfile for optimized image size
- docker-compose with PostgreSQL, Redis, and FastAPI
- Health checks for all services
- Volume mounts for data persistence

```bash
docker-compose up -d
```

#### 8. Comprehensive Testing ✅
- 25+ pytest test cases
- Unit tests for all features
- Mocked external dependencies
- Test coverage for:
  - URL creation and custom aliases
  - Expiration logic
  - Analytics tracking
  - QR code generation
  - Search and filtering
  - API key authentication

## 📦 Installation

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd url_shortner/backend_4
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your database and Redis credentials
```

5. **Run database migrations**
```bash
# The application will create tables automatically on startup
```

6. **Start the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

1. **Build and start all services**
```bash
docker-compose up -d
```

2. **View logs**
```bash
docker-compose logs -f app
```

3. **Stop services**
```bash
docker-compose down
```

## 🧪 Running Tests

```bash
pytest tests/test_url_shortner.py -v
```

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Configuration

### Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/urlshortner
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
ALGORITHAM=HS256
```

### Docker Environment

The `docker-compose.yml` includes pre-configured services:
- **PostgreSQL** on port 5432
- **Redis** on port 6379
- **FastAPI** on port 8000

## 📖 API Endpoints

### Authentication
- `POST /register` - Register new user
- `POST /login` - Login and get tokens
- `POST /token` - OAuth2 compatible token endpoint
- `POST /refresh_token` - Refresh access token
- `POST /logout` - Logout and invalidate refresh token

### URL Management
- `POST /shortner` - Create short URL (with optional alias and expiration)
- `GET /{short_url}` - Redirect to original URL
- `GET /{user_email}/get_all_urls` - List user's URLs (with search/filter)
- `DELETE /delete/{short_url}` - Delete specific URL
- `DELETE /{user_email}/delete_all_urls` - Delete all user URLs

### Analytics
- `GET /analytics/{short_url}` - Get paginated click events
- `GET /analytics/{short_url}/summary` - Get summary with recent clicks

### QR Codes
- `GET /qr/{short_url}` - Get QR code image (PNG)

### API Keys
- `POST /api-keys/` - Create new API key
- `GET /api-keys/` - List all API keys
- `DELETE /api-keys/{id}` - Revoke API key
- `GET /api-keys/verify` - Verify API key (requires X-API-Key header)

## 🏗️ Architecture

### Database Models

**users**
- user_id (Primary Key)
- email
- password (hashed)
- created_at

**UrlShortner**
- id (Primary Key)
- url (Original URL)
- short_url (Unique short code)
- clicks (Total click count)
- created_at
- expires_at (Optional expiration)
- qr_code_path (Path to QR code image)
- user_id (Foreign Key)

**clickanalytic**
- id (Primary Key)
- url_id (Foreign Key)
- clicked_at
- browser
- os
- referrer

**ApiKey**
- id (Primary Key)
- key (Unique API key)
- name (Description)
- user_id (Foreign Key)
- created_at
- last_used_at
- is_active (Boolean)

### Technology Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Reliable relational database
- **Redis** - High-performance caching
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **SlowAPI** - Rate limiting
- **qrcode** - QR code generation
- **user-agents** - Browser/OS detection
- **pytest** - Testing framework
- **Docker** - Containerization

## 🔒 Security Features

- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- Rate limiting on all endpoints
- API key authentication with usage tracking
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM
- Reserved alias protection

## 📊 Performance Optimizations

- Redis caching for frequently accessed URLs
- Background tasks for analytics recording (non-blocking redirects)
- Database indexing on frequently queried fields
- Pagination for large result sets
- Connection pooling for database
- Multi-stage Docker builds for smaller images

## 🚦 Rate Limits

- URL creation: 5 requests/minute
- URL access: 10 requests/minute
- Analytics: 5 requests/minute
- Authentication: 5 requests/minute
- Delete operations: 3-5 requests/minute

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Backend development and architecture
- Feature implementation and testing
- Docker containerization
- Documentation

## 🙏 Acknowledgments

- FastAPI framework and community
- SQLAlchemy ORM
- Redis community
- All open-source contributors

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI**
