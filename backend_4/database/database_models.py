from sqlalchemy import ForeignKey
from sqlalchemy import true
from sqlalchemy import Column, Integer, String, DateTime
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
    user_id=Column(Integer,ForeignKey("user_table.user_id"))

    

class clickanalytic(Base):
    __tablename__="click_analytic"
    id=Column(Integer,primary_key=True,index=True)
    url_id=Column(Integer,ForeignKey("url_shortner.id", ondelete="CASCADE"))
    clicked_at=Column(DateTime,default=datetime.utcnow)
