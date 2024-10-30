from datetime import timedelta

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from dependencies import get_db
from users import models, schemas
from users.security import (create_access_token, get_password_hash,
                            verify_password)

ACCESS_TOKEN_EXPIRE_MINUTES = 500


async def create_user(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.User).where(
        models.User.username == form_data.username)
    )
    user = result.scalars().first()
    if not user or not verify_password(
            form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
