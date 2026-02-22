from ..database import Base
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True)
    header = Column(String)
    content = Column(JSON)
    date = Column(DateTime, default=datetime.utcnow)
    author_id = Column(Integer, ForeignKey("users.id"))
    cover = Column(LargeBinary)
    author = relationship("User", back_populates="news")
    comments = relationship("Comment", back_populates="news")