from ..database import Base
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(Text)
    news_id = Column(Integer, ForeignKey("news.id"))
    date = Column(DateTime)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="comments")
    news = relationship("News", back_populates="comments")