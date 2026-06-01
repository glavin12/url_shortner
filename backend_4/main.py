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
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter=limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(url_shortner_router)
app.include_router(auth_router)

