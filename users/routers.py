from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_db
from users import crud, models, schemas

users_router = APIRouter()


@users_router.post("/register", response_model=schemas.UserResponse)
async def register_user(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
) -> models.User:
    return await crud.create_user(db=db, user=user)


@users_router.post("/login", response_model=schemas.Token)
async def login_user(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
) -> dict:
    return await crud.login_user(form_data=form_data, db=db)
