
from pydantic import BaseModel,Field,EmailStr
from datetime import datetime

class post_url(BaseModel):
    url:str=Field(...,description="this is our main longg url")

class login(BaseModel):
    email: EmailStr
    password:str=Field(min_length=6,max_length=26)


class register(BaseModel):
    name:str=Field("the user name is=ts jsut for the user find it cool")
    email:EmailStr
    password:str=Field(min_length=6,max_length=26)


class response_register(BaseModel):
    name:str=Field("the user name is=ts jsut for the user find it cool")
    email:EmailStr

class refresh_token(BaseModel):
    refresh_token:str=Field()




