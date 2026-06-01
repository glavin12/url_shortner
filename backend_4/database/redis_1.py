from sqlalchemy import delete
import os
import redis
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

redis_url = os.getenv("REDIS_URL")

# Connect with decode_responses=True to automatically handle string conversion
r = redis.Redis.from_url(redis_url, decode_responses=True)


print(r.get("FC5Euk"))
