from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, List
from fastapi import UploadFile

class NewsBase(BaseModel):
    header: str
    content: Dict[str, Any] | List[Any] | str
    cover: UploadFile | None = None

class NewsCreate(NewsBase):
    author_id: int

class NewsRead(NewsCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)