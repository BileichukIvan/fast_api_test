import asyncio
import os
from datetime import datetime

import cohere
from dotenv import load_dotenv
from googleapiclient import discovery
from sqlalchemy import and_, case, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from comments.models import Comment

load_dotenv()

perspective_api_key = os.environ.get("PERSPECTIVE_API_KEY")
cohere_api_key = os.environ.get("COHERE_API_KEY")


async def check_for_toxicity(comment: str):
    client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=perspective_api_key,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    analyze_request = {
        "comment": {"text": comment},
        "requestedAttributes": {"TOXICITY": {}}
    }

    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None, client.comments().analyze(body=analyze_request).execute
    )

    return response["attributeScores"]["TOXICITY"]["spanScores"][0]["score"]["value"] > 0.7


async def get_comments_for_post(db: AsyncSession, post_id: int):
    result = await db.execute(
        select(Comment).filter(Comment.post_id == post_id)
    )
    return result.scalars().all()


async def create_comment(
        db: AsyncSession,
        comment: Comment,
        post_id: int,
        author_id: int
):
    db_comment = Comment(
        content=comment.content,
        post_id=post_id,
        author_id=author_id,
        created_at=datetime.now(),
    )
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def update_comment(
        db: AsyncSession,
        comment: Comment,
        comment_data
):
    comment.content = comment.content or comment_data.content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id: int):
    result = await db.execute(
        select(Comment).filter(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment:
        await db.delete(comment)
        await db.commit()


async def comments_analysis(db: AsyncSession, date_from: str, date_to: str):
    date_from_dt = datetime.strptime(date_from, "%Y-%m-%d")
    date_to_dt = datetime.strptime(date_to, "%Y-%m-%d")

    results = (
        await db.execute(
            select(
                func.strftime("%Y-%m-%d", Comment.created_at).label("day"),
                func.count(Comment.id).label("total_comments"),
                func.sum(
                    case(
                        (Comment.is_blocked == True, 1),
                        else_=0
                    )
                ).label("blocked_comments"),
            )
            .filter(
                and_(Comment.created_at >= date_from_dt,
                     Comment.created_at < date_to_dt)
            )
            .group_by(func.strftime("%Y-%m-%d", Comment.created_at))
            .order_by("day")
        )
    )

    return [
        {
            "day": result.day,
            "total_comments": result.total_comments,
            "blocked_comments": result.blocked_comments or 0,
        }
        for result in results
    ]


async def auto_replay_for_comments(
        db: AsyncSession,
        comment: str,
        post_id: int,
        delay: int,
        author_id: int
):
    co = cohere.ClientV2(cohere_api_key)

    async def generate_reply():
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: co.chat(
                model="command-r-plus",
                messages=[{
                    "role": "user",
                    "content": f"Give a response for this comment: {comment}"
                }]
            )
        )

        reply = response.message[0].content

        db_comment_reply = Comment(
            content=reply, post_id=post_id, author_id=author_id
        )
        db.add(db_comment_reply)
        await db.commit()

    await asyncio.sleep(delay)
    await generate_reply()
