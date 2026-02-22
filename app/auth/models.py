from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)

    token = Column(String, unique=True, index=True)
    user_agent = Column(String)
    ip_address = Column(String)

    created_at = Column(DateTime)
    expires_at = Column(DateTime)
    last_used_at = Column(DateTime)
    revoked_at = Column(DateTime)

    user = relationship("User", back_populates="sessions")
