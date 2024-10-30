import datetime

from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

from database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    auto_replay_enabled = Column(Boolean, default=False)
    auto_replay_delay = Column(Integer, default=0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False
    )
    owner = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
