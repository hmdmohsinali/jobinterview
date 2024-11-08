# app/crud/category.py

from sqlmodel import Session, select
from typing import List, Optional
from app.models.category import Category


def create_category(session: Session, category: Category) -> Category:
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def get_categories(session: Session) -> List[Category]:
    return session.exec(select(Category)).all()


def get_category_by_name(session: Session, category_name: str) -> Optional[Category]:
    statement = select(Category).where(Category.name == category_name)
    return session.exec(statement).first()


def get_category_by_id(session: Session, category_id: int) -> Optional[Category]:
    return session.get(Category, category_id)
