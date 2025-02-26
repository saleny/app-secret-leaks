from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_db
from app.schemas.auth import TokenRequest, TokenResponse
from app.utils.security import create_access_token, verify_password
from app.models.user import User
from app.core.config import settings

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
        request: TokenRequest,
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }