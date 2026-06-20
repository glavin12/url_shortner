from sqlalchemy import ForeignKey, Boolean
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database.database import Base

class users(Base):
    __tablename__="user_table"
    user_id=Column(Integer,primary_key=True,index=True)
    email=Column(String(255),index=True)
    password=Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class UrlShortner(Base):
    __tablename__ = "url_shortner"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(255), index=True)
    short_url = Column(String(255), unique=True, index=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    qr_code_path = Column(String(500), nullable=True)
    user_id=Column(Integer,ForeignKey("user_table.user_id"))

class clickanalytic(Base):
    __tablename__="click_analytic"
    id=Column(Integer,primary_key=True,index=True)
    url_id=Column(Integer,ForeignKey("url_shortner.id", ondelete="CASCADE"))
    clicked_at=Column(DateTime,default=datetime.utcnow)
    browser=Column(String(100), nullable=True)
    os=Column(String(100), nullable=True)
    referrer=Column(Text, nullable=True)

class ApiKey(Base):
    __tablename__="api_keys"
    id=Column(Integer,primary_key=True,index=True)
    key=Column(String(64),unique=True,index=True)
    name=Column(String(100))
    user_id=Column(Integer,ForeignKey("user_table.user_id"))
    created_at=Column(DateTime,default=datetime.utcnow)
    last_used_at=Column(DateTime,nullable=True)
    is_active=Column(Boolean,default=True)
