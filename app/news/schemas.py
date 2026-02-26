from pydantic import BaseModel, ConfigDict
from typing import Any, Dict, List, Optional
from datetime import datetime

class NewsIn(BaseModel):
    header: str
    content: Dict[str, Any] | List[Any] | str

class NewsCreate(NewsIn):
    author_id: Optional[int] = None

class NewsUpdate(BaseModel):
    header: Optional[str] = None
    content: Optional[Dict[str, Any] | List[Any] | str] = None

class NewsRead(NewsCreate):
    id: int
    author_id: int
    author_name: Optional[str]
    date: datetime

    model_config = ConfigDict(from_attributes=True)