# Docker Quick Start Guide

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed ([Get Docker Compose](https://docs.docker.com/compose/install/))

## Quick Start

### 1. Start All Services

From the project root directory:

```bash
docker-compose up -d
```

This will start:
- PostgreSQL database on port 5432
- Redis cache on port 6379
- FastAPI application on port 8000

### 2. Check Service Health

```bash
docker-compose ps
```

All services should show as "healthy" after a few seconds.

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f postgres
docker-compose logs -f redis
```

### 4. Access the Application

- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Test the API

#### Register a User
```bash
curl -X POST "http://localhost:8000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Login
```bash
curl -X POST "http://localhost:8000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

#### Create Short URL (with token)
```bash
curl -X POST "http://localhost:8000/shortner" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "url": "https://example.com",
    "custom_alias": "my-link",
    "expires_at": "2025-12-31T23:59:59"
  }'
```

#### Access Short URL
```bash
curl -L "http://localhost:8000/my-link"
```

#### Get QR Code
```bash
curl "http://localhost:8000/qr/my-link" --output qr.png
```

### 6. Stop Services

```bash
docker-compose down
```

### 7. Stop and Remove All Data

```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If ports 5432, 6379, or 8000 are already in use, modify `docker-compose.yml`:

```yaml
services:
  postgres:
    ports:
      - "5433:5432"  # Change 5432 to 5433
  
  redis:
    ports:
      - "6380:6379"  # Change 6379 to 6380
  
  app:
    ports:
      - "8001:8000"  # Change 8000 to 8001
```

### Check Container Logs

```bash
docker-compose logs app
```

### Restart Specific Service

```bash
docker-compose restart app
```

### Rebuild After Code Changes

```bash
docker-compose up -d --build
```

### Access Database Directly

```bash
docker-compose exec postgres psql -U postgres -d urlshortner
```

### Access Redis CLI

```bash
docker-compose exec redis redis-cli
```

## Production Deployment

### 1. Update Environment Variables

Edit `docker-compose.yml` and set secure credentials:

```yaml
environment:
  DATABASE_URL: "postgresql://secure_user:secure_password@postgres:5432/urlshortner"
  SECRET_KEY: "generate-a-secure-random-key-here"
```

### 2. Use Production Redis

Replace Redis service with a managed Redis instance (e.g., AWS ElastiCache, Redis Cloud):

```yaml
environment:
  REDIS_URL: "rediss://your-production-redis-url"
```

### 3. Add SSL/TLS

Use a reverse proxy (Nginx, Traefik) to handle SSL:

```yaml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
```

### 4. Enable Monitoring

Add health check endpoints and monitoring services.

### 5. Backup Database

```bash
docker-compose exec postgres pg_dump -U postgres urlshortner > backup.sql
```

## Performance Tuning

### Scale Application Instances

```bash
docker-compose up -d --scale app=3
```

### Configure PostgreSQL

Create `postgres.conf` and mount it:

```yaml
volumes:
  - ./postgres.conf:/etc/postgresql/postgresql.conf
```

### Configure Redis

Create `redis.conf` and mount it:

```yaml
volumes:
  - ./redis.conf:/usr/local/etc/redis/redis.conf
```

## Development Workflow

### Hot Reload

Mount source code for development:

```yaml
services:
  app:
    volumes:
      - ./backend_4:/app
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests in Container

```bash
docker-compose exec app pytest tests/ -v
```

### Access Python Shell

```bash
docker-compose exec app python
```

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart app

# Rebuild and start
docker-compose up -d --build

# Check status
docker-compose ps

# Execute command in container
docker-compose exec app <command>

# Remove all containers and volumes
docker-compose down -v
```

## Next Steps

- Read the main [README_FEATURES.md](README_FEATURES.md) for API documentation
- Visit http://localhost:8000/docs for interactive API documentation
- Check test cases in `tests/` for usage examples
- Review `routes/` directory for endpoint implementations

---

**Need help?** Open an issue on GitHub!
