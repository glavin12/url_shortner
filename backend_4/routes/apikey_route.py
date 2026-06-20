from fastapi import APIRouter, Depends, HTTPException, Request, Header
from database.database_models import ApiKey, users
from database.database import get_db
from database.schemas import ApiKeyCreate, ApiKeyResponse
from auth.auth_jwt import verify_access_token
from limiter import limiter
from datetime import datetime
import secrets
from typing import Optional

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

def generate_api_key() -> str:
    """Generate a secure random API key"""
    return f"sk_{secrets.token_urlsafe(32)}"

async def verify_api_key(x_api_key: str = Header(None), db = Depends(get_db)):
    """Dependency to verify API key authentication"""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key is required. Provide X-API-Key header."
        )
    
    api_key_obj = db.query(ApiKey).filter(
        ApiKey.key == x_api_key,
        ApiKey.is_active == True
    ).first()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=401,
            detail="Invalid or inactive API key"
        )
    
    # Update last_used_at timestamp
    api_key_obj.last_used_at = datetime.utcnow()
    db.commit()
    
    return {
        "user_id": api_key_obj.user_id,
        "api_key_id": api_key_obj.id
    }

@router.post("/", response_model=ApiKeyResponse)
@limiter.limit("5/minute")
def create_api_key(
    api_key_data: ApiKeyCreate,
    request: Request,
    db = Depends(get_db),
    current_user = Depends(verify_access_token)
):
    """Create a new API key for the authenticated user"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    key = generate_api_key()
    api_key = ApiKey(
        key=key,
        name=api_key_data.name,
        user_id=user_id
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key

@router.get("/", response_model=list[ApiKeyResponse])
@limiter.limit("5/minute")
def list_api_keys(
    request: Request,
    db = Depends(get_db),
    current_user = Depends(verify_access_token)
):
    """List all API keys for the authenticated user"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == user_id).all()
    return api_keys

@router.delete("/{api_key_id}")
@limiter.limit("5/minute")
def revoke_api_key(
    api_key_id: int,
    request: Request,
    db = Depends(get_db),
    current_user = Depends(verify_access_token)
):
    """Revoke (deactivate) an API key"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    api_key = db.query(ApiKey).filter(
        ApiKey.id == api_key_id,
        ApiKey.user_id == user_id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=404,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"}

@router.get("/verify")
@limiter.limit("10/minute")
def verify_api_key_endpoint(
    request: Request,
    current_user = Depends(verify_api_key)
):
    """Verify if an API key is valid"""
    return {
        "valid": True,
        "user_id": current_user["user_id"]
    }
