from database.database import Base, engine
import database.database_models

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from limiter import limiter

from routes.url_shortner import router as url_shortner_router
from routes.auth_route import router as auth_router
from routes.apikey_route import router as apikey_router
app = FastAPI()

import os

# Get frontend URL from environment variable, default to common development ports
frontend_urls = os.getenv("FRONTEND_URLS", "http://localhost:5173,http://localhost:3000,https://pretty-laughter-production.up.railway.app").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_urls,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter=limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(url_shortner_router)
app.include_router(auth_router)
app.include_router(apikey_router)

