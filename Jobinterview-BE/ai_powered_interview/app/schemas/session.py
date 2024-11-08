# app/schemas/session.py

from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class SessionCreate(SQLModel):
    pass  # Add fields if necessary

class SessionRead(SQLModel):
    id: int
    user_id: int
    category_id: int
    current_question: Optional[str]
    completed: bool
    started_at: datetime
