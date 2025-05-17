from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import User, Token, UserProfile
from utils.auth_utils import create_access_token, create_refresh_token, verify_password, hash_password
from datetime import datetime, timedelta
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

from decorator.jwt_decorator import jwt_authorization

from routers.request_models.user_models import UserCreate, UserLogin

router = APIRouter()

@router.post("/signup/")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username or email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password before storing
    hashed_password = hash_password(user.password)

    # Create new user
    new_user = User(email=user.email, password=hashed_password, is_admin = 0, is_staff = 0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create empty profile for the user
    new_profile = UserProfile(user_id=new_user.user_id)
    db.add(new_profile)
    db.commit()

    return {"msg": "User created successfully", "user_id": new_user.user_id}

@router.post("/login/")
async def login(request: UserLogin, db: Session = Depends(get_db)):
    try:
        # Get user with a single query
        db_user = (
            db.query(User)
            .filter(User.email == request.email)
            .first()
        )
        
        # Early return if user doesn't exist or password is wrong
        if not db_user or not verify_password(request.password, db_user.password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        # Parse environment variables with error handling
        try:
            access_token_expire_minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token_expire_days = int(REFRESH_TOKEN_EXPIRE_DAYS)
        except ValueError:
            raise HTTPException(
                status_code=500,
                detail="Invalid token expiration configuration"
            )

        # Calculate token expiration times
        current_time = datetime.utcnow()
        access_token_expires = timedelta(minutes=access_token_expire_minutes)
        refresh_token_expires = timedelta(days=refresh_token_expire_days)

        
        token_data = {
            "user_id": db_user.user_id,
            "is_admin": db_user.is_admin if db_user.is_admin is not None else 0,
            "is_staff": db_user.is_staff if db_user.is_admin is not None else 0,
            "type": "access"  # Add token type for additional security
        }
        refresh_token_data = {
            "user_id": db_user.user_id,
            "is_admin": db_user.is_admin,
            "is_staff": db_user.is_staff,
            "type": "refresh"
        }

        # Generate tokens
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data=refresh_token_data,
            expires_delta=refresh_token_expires
        )


        # Use a transaction for database operations
        try:
            # Remove old tokens
            # Check if tokens exist before deleting
            existing_tokens = db.query(Token).filter(Token.user_id == db_user.user_id).all()
            if existing_tokens:
                db.query(Token).filter(Token.user_id == db_user.user_id).delete()

            # Add new tokens
            db.add_all([
                Token(
                    user_id=db_user.user_id,
                    token_type="access",
                    token=access_token,
                    expires_at=current_time + access_token_expires
                ),
                Token(
                    user_id=db_user.user_id,
                    token_type="refresh",
                    token=refresh_token,
                    expires_at=current_time + refresh_token_expires
                )
            ])
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Error while processing authentication"
            )

        return {
            "user_id": db_user.user_id,
            "is_admin": db_user.is_admin,
            "is_staff": db_user.is_staff,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_token_expire_minutes * 60  # Return expiration in seconds
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )
    

@router.post("/logout/")
def logout(
    token_data: dict = Depends(jwt_authorization),
    db: Session = Depends(get_db)
):

    # Find the token and delete it (invalidate)
    token = db.query(Token).filter(Token.user_id == token_data.user_id).first()
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    try:
        # Delete all tokens for this user (optional: or just the current token)
        db.query(Token).filter(Token.user_id == token.user_id).delete()
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error during logout")

    return {"msg": "Successfully logged out"}
