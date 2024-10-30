from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from posts import models, schemas


async def create_post(db: AsyncSession, post_data: schemas.PostCreate, user_id: int):
    new_post = models.Post(
        title=post_data.title,
        content=post_data.content,
        owner_id=user_id,
        auto_replay_enabled=post_data.auto_replay_enabled,
        auto_replay_delay=post_data.auto_replay_delay,
        created_at=datetime.now()
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


async def get_post_by_id(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(models.Post).filter(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


async def get_posts(db: AsyncSession):
    result = await db.execute(select(models.Post))
    posts = result.scalars().all()
    if posts:
        return posts
    return []


async def update_post(
        db: AsyncSession,
        post_id: int,
        post_data: schemas.PostResponse
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data_dict = post_data.dict(exclude_unset=True)

    for key, value in post_data_dict.items():
        if key != "_sa_instance_state":
            setattr(post, key, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(db: AsyncSession, post_id: int):
    post = await get_post_by_id(db, post_id)
    await db.delete(post)
    await db.commit()
    return {"message": "Post deleted successfully"}
