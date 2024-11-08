# app/schemas/answer.py

from sqlmodel import SQLModel
from datetime import datetime

class AnswerCreate(SQLModel):
    answer_text: str

class AnswerRead(SQLModel):
    id: int
    session_id: int
    question: str
    answer_text: str
    feedback: str
    submitted_at: datetime
