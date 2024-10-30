from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from comments import crud, models, schemas
from dependencies import get_db
from posts.models import Post
from users import models, security

comments_router = APIRouter()


@comments_router.get(
    "/comments/{post_id}", response_model=List[schemas.Comment]
)
async def get_comments_for_post(post_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Comment).filter(
        models.Comment.post_id == post_id)
    )
    comments = result.scalars().all()
    if not comments:
        raise HTTPException(status_code=404, detail="Comments not found")
    return comments


@comments_router.post(
    "/posts/{post_id}/comments", response_model=schemas.Comment
)
async def create_comment(
        post_id: int,
        comment: schemas.CommentCreate,
        user: models.User = Depends(security.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post).filter(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    toxicity = await crud.check_for_toxicity(comment.content)

    db_comment = models.Comment(
        content=comment.content,
        post_id=post_id,
        author_id=user.id,
        is_blocked=toxicity
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)

    if post.auto_replay_enabled:
        await crud.auto_replay_for_comments(
            db,
            comment.content,
            post_id,
            post.auto_replay_delay,
            post.user_id
        )

    return db_comment


@comments_router.put("/comments/{comment_id}", response_model=schemas.Comment)
async def update_comment(
        comment_id: int,
        comment_data: schemas.Comment,
        user: models.User = Depends(security.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Comment).filter(
        models.Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to edit this comment"
        )

    toxicity = await crud.check_for_toxicity(comment_data.content)
    if toxicity:
        comment.is_blocked = toxicity

    return await crud.update_comment(
        db=db, comment_data=comment_data, comment=comment
    )


@comments_router.delete(
    "/comments/{comment_id}",
    response_model=schemas.Comment
)
async def delete_comment(
        comment_id: int,
        user: models.User = Depends(security.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Comment).filter(
        models.Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to delete this comment")

    await crud.delete_comment(db=db, comment_id=comment_id)


@comments_router.get(
    "/comments/comments-daily-breakdown/", response_model=List[dict]
)
async def get_comments_daily_breakdown(
        date_from: str,
        date_to: str,
        db: AsyncSession = Depends(get_db),
):
    return await crud.comments_analysis(
        db=db, date_from=date_from, date_to=date_to
    )
