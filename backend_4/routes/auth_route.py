from anyio import from_thread
from asyncio import base_futures
from auth.auth_jwt import create_refresh_token,verify_refresh_token
from auth.auth_jwt import create_access_token
from fastapi import APIRouter, Depends, HTTPException,Request
from fastapi.security import OAuth2PasswordRequestForm
from database.redis_1 import r
from database.schemas import refresh_token
from database.database import get_db
from limiter import limiter

from database.schemas import (
    register,
    login,
    response_register
)

from auth.hashed_password import (
    hash_password,
    verify_password
)

from database.database_models import (
    users,
    UrlShortner
)

router = APIRouter()


@router.post(
    "/register",
    response_model=response_register
)
@limiter.limit("5/minute")
def register_user(
    user: register,
    request: Request,
    db=Depends(get_db)
):

    hashed_password = hash_password(
        user.password
    )

    user_obj = users(
        password=hashed_password,
        email=user.email
    )

    db.add(user_obj)

    db.commit()

    db.refresh(user_obj)

    return user_obj

@router.post('/login')
@limiter.limit("5/minute")
def login_user(user:login,request:Request,db=Depends(get_db)):

    user_obj=db.query(users).filter(user.email==users.email).first()
    if not user_obj:
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )

    valid_password=verify_password(
        user.password,
        user_obj.password
    )
    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="password is incorrect"
        )

    access_token=create_access_token({
        "sub":user_obj.email,
        "user_id":user_obj.user_id,
        "type": "ACCESS"
    })
    refresh_token=create_refresh_token({
        "sub":user_obj.email,
        "user_id":user_obj.user_id,
        "type": "REFRESH"
    })
    r.set(f"refresh:{user_obj.user_id}",refresh_token,ex=604800)
    
    return{
        "access_token":access_token,
        "refresh_token":refresh_token,
        "token_type":"bearer"
    }

@router.post("/logout")
@limiter.limit("10/minute")
def logout(request: Request, current_user=Depends(verify_refresh_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )
    r.delete(f"refresh:{current_user['user_id']}")
    return {
        "message":"user logged out successfully"
    }    

@router.post("/token")
@limiter.limit("5/minute")
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db = Depends(get_db)
):
    user_obj = db.query(users).filter(users.email == form_data.username).first()
    if not user_obj:
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )

    valid_password = verify_password(
        form_data.password,
        user_obj.password
    )
    if not valid_password:
        raise HTTPException(
            status_code=401,
            detail="password is incorrect"
        )

    access_token = create_access_token({
        "sub": user_obj.email,
        "user_id": user_obj.user_id,
        "type": "ACCESS"
    })
    refresh_token = create_refresh_token({
        "sub": user_obj.email,
        "user_id": user_obj.user_id,
        "type": "REFRESH"
    })
    r.set(f"refresh:{user_obj.user_id}", refresh_token, ex=604800)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    } 


@router.post("/refresh_token")
@limiter.limit("10/minute")
def get_new_access_token(request: Request, current_user=Depends(verify_refresh_token)):
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="invalid credentials"
        )
    access_token=create_access_token({
        "sub":current_user["sub"],
        "user_id":current_user["user_id"],
        "type": "ACCESS"
    })
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }    





