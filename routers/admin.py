from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Dict
from database.session import get_db
from database.models import User
from datetime import datetime, timedelta
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from decorator.jwt_decorator import jwt_authorization

router = APIRouter()


@router.get("/get-all-users")
def get_all_user(
    db: Session = Depends(get_db), 
    token_data: dict = Depends(jwt_authorization)  # Extracting token data
):
    # Checking if the user is admin
    if not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission denied")

    all_users = db.query(User).filter(User.is_admin != 1).all()

    if not all_users:
        raise HTTPException(status_code=404, detail="Users not found")

    return {"user": all_users}


@router.delete("/delete-user/{user_id}")
def delete_user(
    user_id: int, 
    db: Session = Depends(get_db), 
    token_data: dict = Depends(jwt_authorization)  # Extracting token data
):
    # Checking if the user is admin
    if not token_data.get("is_admin"):
        raise HTTPException(status_code=403, detail="Permission denied")

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}