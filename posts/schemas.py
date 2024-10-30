from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    auto_replay_enabled: bool
    auto_replay_delay: int


class PostCreate(PostBase):
    pass


class PostResponse(BaseModel):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
