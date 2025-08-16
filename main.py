import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.homepage import homepage
from app.post import post
from app.user import user
from app.database import database


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.setup_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(homepage.router)
app.include_router(post.router)
app.include_router(user.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
