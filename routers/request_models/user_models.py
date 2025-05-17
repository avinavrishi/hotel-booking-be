from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Pydantic Models for Request Validation
class UserCreate(BaseModel):
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[datetime] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    nationality: Optional[str] = None
    preferred_language: Optional[str] = None