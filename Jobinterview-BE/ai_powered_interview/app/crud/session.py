# app/crud/session.py

from sqlmodel import Session, select
from typing import Optional, List
from app.models.session import Session as InterviewSession
from app.models.answer import Answer


def create_session(session: Session, session_data: InterviewSession) -> InterviewSession:
    session.add(session_data)
    session.commit()
    session.refresh(session_data)
    return session_data


def get_session(session: Session, session_id: int) -> Optional[InterviewSession]:
    return session.get(InterviewSession, session_id)


def add_answer(session: Session, answer: Answer) -> Answer:
    session.add(answer)
    session.commit()
    session.refresh(answer)
    return answer


def get_answers(session: Session, session_id: int) -> List[Answer]:
    statement = select(Answer).where(Answer.session_id == session_id)
    return session.exec(statement).all()
