# app/schemas/category.py

from sqlmodel import SQLModel

class CategoryCreate(SQLModel):
    name: str

class CategoryRead(SQLModel):
    id: int
    name: str
