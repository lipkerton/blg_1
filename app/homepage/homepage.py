"""
Заготовка под главную страницу.
Я пока не знаю, что тут сделать.
"""
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def homepage():
    """
    Пока возвращает простой словарь.
    """
    return {"message": "Hello!"}
