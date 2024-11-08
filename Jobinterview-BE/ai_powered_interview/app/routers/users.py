# app/routers/users.py

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from app.crud.user import create_user, authenticate_user
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.schemas.token import Token
from app.dependencies import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", response_model=UserRead)
def register_user(user_create: UserCreate, session: Session = Depends(get_session)):
    """
    Registers a new user.

    **Endpoint:** POST /users/register

    **Request Body:**
    {
      "username": "john_doe",
      "email": "john@example.com",
      "password": "securepassword"
    }

    **Response:**
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-10-26T12:00:00"
    }
    """
    user = User(
        username=user_create.username,
        email=user_create.email,
    )
    try:
        user = create_user(session, user, user_create.password)
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    return user


@router.post("/login", response_model=Token)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    """
    Authenticates a user and returns a JWT token set in an HTTP-only cookie.

    **Endpoint:** POST /users/login

    **Request Body (Form Data):**
    - **username**: User's username.
    - **password**: User's password.

    **Response:**
    {
      "access_token": "<token>",
      "token_type": "bearer"
    }
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Set the JWT token in an HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(response: Response):
    """
    Logs out the user by clearing the JWT cookie.

    **Endpoint:** POST /users/logout

    **Response:**
    {
      "message": "Successfully logged out."
    }
    """
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out."}
