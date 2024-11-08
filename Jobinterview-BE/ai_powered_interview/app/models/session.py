# app/models/session.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class Session(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    category_id: int = Field(foreign_key="category.id")
    current_question: Optional[str] = None
    completed: bool = Field(default=False)
    started_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="sessions")
    category: Optional["Category"] = Relationship(back_populates="sessions")
    answers: List["Answer"] = Relationship(back_populates="session")
