from fastapi import APIRouter, Response


router = APIRouter()


@router.post("/login")
async def login():
    pass
