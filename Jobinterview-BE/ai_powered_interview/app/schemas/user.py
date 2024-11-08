# app/schemas/user.py

from sqlmodel import SQLModel
from datetime import datetime
from pydantic import EmailStr

class UserCreate(SQLModel):
    username: str
    email: EmailStr
    password: str

class UserRead(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
