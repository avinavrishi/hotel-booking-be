# schemas/user.py

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProfileResponse(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    nationality: Optional[str] = None
    preferred_language: Optional[str] = "en"

    class Config:
        orm_mode = True

class UserResponse(BaseModel):
    user_id: int
    email: str
    is_admin: Optional[int] = None
    is_staff: Optional[int] = None
    profile: Optional[UserProfileResponse] = None

    class Config:
        orm_mode = True
