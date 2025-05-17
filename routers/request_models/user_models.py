from pydantic import BaseModel, EmailStr

# Pydantic Models for Request Validation
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr  # Ensuring valid email format

class UserLogin(BaseModel):
    username: str
    password: str