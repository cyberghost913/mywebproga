from pydantic import BaseModel

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    news_id: int

class CommentRead(CommentCreate):
    id: int
    author_id: int