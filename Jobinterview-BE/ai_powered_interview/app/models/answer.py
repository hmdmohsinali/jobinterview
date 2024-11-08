# app/models/answer.py

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="session.id")
    question: str
    answer_text: str
    feedback: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    session: Optional["Session"] = Relationship(back_populates="answers")
