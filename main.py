from fastapi import FastAPI

from comments.routers import comments_router
from dependencies import create_db_and_tables
from posts.routers import posts_router
from users.routers import users_router

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()

app.include_router(users_router)
app.include_router(posts_router)
app.include_router(comments_router)
