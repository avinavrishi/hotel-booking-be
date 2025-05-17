# decorators.py
import jwt
from functools import wraps
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import User, Token
from fastapi import Header, HTTPException, Depends

from core.config import SECRET_KEY


def jwt_authorization(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer token not provided")

    token = authorization.split("Bearer ")[1]
    try:
        login_detail = db.query(Token).filter(Token.token == token).first()
        if login_detail is None:
             raise HTTPException(status_code=401, detail="Invalid token")

        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")

        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
             raise HTTPException(status_code=404, detail="User not found")

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"user_id": user_id, "is_admin": user.is_admin, "is_staff": user.is_staff}