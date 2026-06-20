
from pydantic import BaseModel,Field,EmailStr
from datetime import datetime
from typing import Optional

class post_url(BaseModel):
    url:str=Field(...,description="this is our main longg url")
    custom_alias:str | None = Field(
        default=None,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="Optional custom alias for the short URL (letters, numbers, hyphens, underscores only)"
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        description="Optional expiration date for the short URL"
    )

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

class ApiKeyCreate(BaseModel):
    name:str=Field(...,min_length=1,max_length=100,description="Name/description for this API key")

class ApiKeyResponse(BaseModel):
    id:int
    key:str
    name:str
    created_at:datetime
    last_used_at:Optional[datetime]
    is_active:bool
    
    class Config:
        from_attributes = True

class AnalyticsClick(BaseModel):
    id:int
    clicked_at:datetime
    browser:Optional[str]
    os:Optional[str]
    referrer:Optional[str]
    
    class Config:
        from_attributes = True

class AnalyticsSummary(BaseModel):
    total_clicks:int
    recent_clicks:list[AnalyticsClick]




