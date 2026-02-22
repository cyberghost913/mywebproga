from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    is_admin: bool = False
    is_active: bool = True
    is_author: bool = False

class SessionInfo(BaseModel):
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None

class AccessToken(BaseModel):
    value: str
    type: str = "Bearer"
    refresh_token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenPayload(User):
    iat: datetime
    exp: datetime

    @field_serializer("iat", "exp", when_used="json")
    def to_timestamp(self, value: datetime) -> float:
        return value.timestamp()