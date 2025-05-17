from pydantic import BaseModel, EmailStr

# Pydantic Models for Request Validation
class UserCreate(BaseModel):
    password: str
    email: EmailStr

class UserLogin(BaseModel):
    email: EmailStr
    password: str