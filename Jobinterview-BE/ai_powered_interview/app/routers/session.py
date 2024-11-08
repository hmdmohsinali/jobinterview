# app/routers/session.py

from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, List
from sqlmodel import Session
from app.crud.session import (
    create_session as create_interview_session,
    get_session as get_interview_session,
    add_answer,
    get_answers
)
from app.crud.category import get_category_by_id
from app.schemas.session import SessionCreate, SessionRead
from app.schemas.answer import AnswerCreate
from app.schemas.feedback import (
    FinalFeedbackItem,
    CompletionResponse,
    NextQuestionResponse,
    ResponseModel
)
from app.database import get_session
from app.services.langchain import generate_question, generate_feedback
from app.dependencies import get_current_user
from app.models.user import User
from app.models.session import Session as InterviewSession
from app.models.answer import Answer
from app.models.category import Category

router = APIRouter(prefix="/session", tags=["Session"])


@router.post("/init", response_model=SessionRead)
async def initialize_session(
    session_create: SessionCreate,
    db: Session = Depends(get_session),
    category_id: Optional[int] = Header(
        None,
        alias="X-Category-ID",
        description="ID of the category",
        title="Category ID"
    ),
    current_user: User = Depends(get_current_user)
):
    if category_id is None:
        raise HTTPException(status_code=400, detail="X-Category-ID header is required.")

    user_id = current_user.id

    category = get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    try:
        question = await generate_question(category.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate question.") from e

    interview_session = InterviewSession(
        user_id=user_id,
        category_id=category.id,
        current_question=question
    )
    interview_session = create_interview_session(db, interview_session)
    return interview_session


@router.post("/answer", response_model=ResponseModel)
async def submit_answer(
    answer_create: AnswerCreate,
    db: Session = Depends(get_session),
    session_id: Optional[int] = Header(None, description="Session ID"),
    category_id: Optional[int] = Header(
        None,
        alias="X-Category-ID",
        description="Category ID"
    ),
    current_user: User = Depends(get_current_user)
):
    if session_id is None:
        raise HTTPException(status_code=400, detail="Session-ID header is required.")

    if category_id is None:
        raise HTTPException(status_code=400, detail="X-Category-ID header is required.")

    interview_session = get_interview_session(db, session_id)
    if not interview_session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if interview_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session.")

    if interview_session.category_id != category_id:
        raise HTTPException(
            status_code=400,
            detail="Provided Category ID does not match the session's Category ID."
        )

    if interview_session.completed:
        raise HTTPException(status_code=400, detail="Session already completed.")

    if not interview_session.current_question:
        raise HTTPException(status_code=400, detail="No current question to answer.")

    try:
        feedback = await generate_feedback(interview_session.current_question, answer_create.answer_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate feedback.") from e

    if feedback is None or feedback.strip() == "":
        raise HTTPException(status_code=500, detail="Failed to generate feedback for the answer.")

    answer = Answer(
        session_id=interview_session.id,
        question=interview_session.current_question,
        answer_text=answer_create.answer_text,
        feedback=feedback
    )
    add_answer(db, answer)

    answers = get_answers(db, interview_session.id)
    answers_count = len(answers)

    max_questions = 5
    if answers_count >= max_questions:
        interview_session.completed = True
        interview_session.current_question = None
        db.add(interview_session)
        db.commit()
        db.refresh(interview_session)

        return CompletionResponse(
            message="Session completed",
        )

    category = get_category_by_id(db, interview_session.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found.")

    try:
        next_question = await generate_question(category.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate next question.") from e

    interview_session.current_question = next_question
    db.add(interview_session)
    db.commit()
    db.refresh(interview_session)

    return NextQuestionResponse(
        next_question=next_question
    )


@router.get("/final", response_model=List[FinalFeedbackItem])
def get_final_feedback(
    db: Session = Depends(get_session),
    session_id: Optional[int] = Header(None, description="Session ID"),
    current_user: User = Depends(get_current_user)
):
    if session_id is None:
        raise HTTPException(status_code=400, detail="Session-ID header is required.")

    interview_session = get_interview_session(db, session_id)
    if not interview_session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if interview_session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session.")

    if not interview_session.completed:
        raise HTTPException(status_code=400, detail="Session not completed yet.")

    answers = get_answers(db, session_id)
    final_feedback = [
        FinalFeedbackItem(
            question=answer.question,
            answer=answer.answer_text,
            feedback=answer.feedback
        )
        for answer in answers
    ]
    return final_feedback
