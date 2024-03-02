from sqlalchemy import Column, Integer, String
from .database import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    history = Column(String)
