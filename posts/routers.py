from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from posts import crud, schemas
from users.models import User
from users.security import get_current_user

posts_router = APIRouter()


@posts_router.post("/posts/", response_model=schemas.PostCreate)
async def create_post(
        post_data: schemas.PostCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    return await crud.create_post(
        db=db,
        user_id=current_user.id,
        post_data=post_data
    )


@posts_router.get("/posts/", response_model=schemas.PostResponse)
async def get_posts(db: AsyncSession = Depends(get_db)):
    return await crud.get_posts(db=db)


@posts_router.get("/posts/{post_id}", response_model=schemas.PostResponse)
async def get_post(
        post_id: int,
        db: AsyncSession = Depends(get_db)
):
    result = await crud.get_post_by_id(post_id=post_id, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@posts_router.put("/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(
        post_data: schemas.PostResponse,
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    post = await crud.get_post_by_id(post_id=post_id, db=db)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found or not authorized"
        )
    if current_user.id != post.owner_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update this post"
        )
    return await crud.update_post(db=db, post_id=post_id, post_data=post_data)


@posts_router.delete("/posts/{post_id}")
async def delete_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    post = await crud.get_post_by_id(post_id=post_id, db=db)
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found or not authorized"
        )
    if current_user.id != post.owner_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this post"
        )
    return await crud.delete_post(db=db, post_id=post_id)
