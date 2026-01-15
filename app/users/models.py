from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, LargeBinary, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, unique=True, index=True)
    password = Column(String, nullable=True)

    github_id = Column(String, unique=True, nullable=True)

    is_author = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    date = Column(DateTime)
    ava = Column(LargeBinary, nullable=True)
    is_active = Column(Boolean, default=True)

    news = relationship("News", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    sessions = relationship("Session", back_populates="user")