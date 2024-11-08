# app/schemas/feedback.py

from pydantic import BaseModel
from typing import Union

class FinalFeedbackItem(BaseModel):
    question: str
    answer: str
    feedback: str

class CompletionResponse(BaseModel):
    message: str

class NextQuestionResponse(BaseModel):
    next_question: str

ResponseModel = Union[CompletionResponse, NextQuestionResponse]
