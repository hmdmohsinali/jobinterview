# app/routers/categories.py

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlmodel import Session
from app.crud.category import (
    create_category,
    get_categories,
    get_category_by_name
)
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead
from app.database import get_session
from app.models.user import User
from app.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryRead)
def create_new_category(
    category: CategoryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Optionally, implement role-based access control here

    existing_category = get_category_by_name(session, category.name)
    if existing_category:
        raise HTTPException(status_code=400, detail="Category already exists.")

    db_category = Category(name=category.name)
    return create_category(session, db_category)


@router.get("/", response_model=List[CategoryRead])
def read_categories(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    categories = get_categories(session)
    return categories
