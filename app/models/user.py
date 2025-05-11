from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime, func, Boolean

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    primary_language = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    is_active = Column(Boolean, default=True)