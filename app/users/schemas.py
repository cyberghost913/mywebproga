from pydantic import BaseModel, ConfigDict
from typing import Optional
from fastapi import UploadFile

class UserBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    ava: UploadFile | None = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    username: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)