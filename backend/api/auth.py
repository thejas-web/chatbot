from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.core.security import (
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ADMIN_USERNAME,
    ADMIN_PASSWORD_HASH,
)


router = APIRouter()


# ==================================================
# LOGIN REQUEST
# ==================================================

class LoginRequest(BaseModel):
    username: str
    password: str


# ==================================================
# LOGIN RESPONSE
# ==================================================

class LoginResponse(BaseModel):
    access_token: str
    token_type: str


# ==================================================
# ADMIN LOGIN
# ==================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(request: LoginRequest):

    # ----------------------------------------------
    # CHECK USERNAME
    # ----------------------------------------------

    if request.username != ADMIN_USERNAME:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    # ----------------------------------------------
    # CHECK PASSWORD
    # ----------------------------------------------

    password_valid = verify_password(
        request.password,
        ADMIN_PASSWORD_HASH,
    )

    if not password_valid:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    # ----------------------------------------------
    # CREATE JWT
    # ----------------------------------------------

    access_token = create_access_token(
        data={
            "sub": ADMIN_USERNAME,
            "role": "admin",
        },
        expires_delta=timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    )

    # ----------------------------------------------
    # RETURN TOKEN
    # ----------------------------------------------

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }