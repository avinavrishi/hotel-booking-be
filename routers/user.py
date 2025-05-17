from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, UserProfile
from decorator.jwt_decorator import jwt_authorization

from routers.request_models.user_models import UserUpdate, UserProfileUpdate  # Assumed schemas
from utils.auth_utils import hash_password

router = APIRouter()


@router.get("/users/me")
def get_current_user_profile(
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/me")
def update_current_user_info(
    updates: UserUpdate,
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == token_data["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if updates.email:
        user.email = updates.email
    if updates.password:
        user.password = hash_password(updates.password)

    db.commit()
    db.refresh(user)
    return {"msg": "User info updated", "user": user}


@router.get("/users/{user_id}/profile")
def get_user_profile(
    user_id: int = Path(..., gt=0),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/users/{user_id}/profile")
def create_user_profile(
    profile_data: UserProfileUpdate,
    user_id: int = Path(..., gt=0),
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if token_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = UserProfile(user_id=user_id, **profile_data.dict())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"msg": "Profile created", "profile": profile}


@router.put("/users/{user_id}/profile")
def update_user_profile(
    profile_data: UserProfileUpdate,
    user_id: int = Path(..., gt=0),
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if token_data["user_id"] != user_id and not token_data.get("is_admin", 0):
        raise HTTPException(status_code=403, detail="Not authorized")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return {"msg": "Profile updated", "profile": profile}


@router.delete("/users/{user_id}/profile")
def delete_user_profile(
    user_id: int = Path(..., gt=0),
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):
    if not token_data.get("is_admin", 0):
        raise HTTPException(status_code=403, detail="Admin access required")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()
    return {"msg": "Profile deleted"}
