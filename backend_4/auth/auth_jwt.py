from jose.exceptions import JWTError
from jose import jwt
from  datetime import datetime,timedelta
import os
from dotenv import load_dotenv
load_dotenv()
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")
secretkey=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHAM")
from database.database import get_db
from database.database_models import users
from database.redis_1 import r
def create_access_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(hours=1)

    to_encode.update({
        "exp":expire
    })

    return jwt.encode(
        to_encode,secretkey,
        algorithm=ALGORITHM
    )




def create_refresh_token(data:dict):
    to_encode=data.copy()
    expire=datetime.utcnow()+timedelta(days=7)

    to_encode.update(
       { "exp":expire}
    )

    return jwt.encode(to_encode,secretkey,algorithm=ALGORITHM)


def verify_access_token(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(
            token,secretkey,algorithms=ALGORITHM
        )

        token_type=payload.get("type")
        if token_type!="ACCESS":
            return None


        return payload          
    except JWTError:
        return None


def verify_refresh_token(token:str=Depends(oauth2_scheme)):
    try:
        payload=jwt.decode(
            token,secretkey,algorithms=ALGORITHM
        )

        token_type=payload.get("type")
        if token_type!="REFRESH":
            return None

        user_id=payload.get("user_id")
        if not user_id:
            return None

        if r.get(f"refresh:{user_id}")!=token:
            return None

        return payload         
    except JWTError:
        return None  