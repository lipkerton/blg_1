"""
main.py
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.homepage import homepage
from app.post import post
from app.user import user



# @asynccontextmanager
# async def lifespan(app: FastAPI):  # pylint: disable=unused-argument, disable=redefined-outer-name
#     """
#     Инициализация БД при старте приложения.
#     """
#     await database.setup_db()
#     yield
#

app = FastAPI()
app.include_router(homepage.router)
app.include_router(post.router)
app.include_router(user.router)

app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
