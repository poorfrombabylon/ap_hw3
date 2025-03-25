from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class LinkCreate(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

class LinkUpdate(BaseModel):
    original_url: str

class LinkInfo(BaseModel):
    original_url: str
    short_code: str
    click_count: int
    created_at: datetime
    last_accessed: Optional[datetime]

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"