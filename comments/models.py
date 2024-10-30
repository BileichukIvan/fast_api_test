import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    is_blocked = Column(Boolean, default=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.UTC),
        nullable=False
    )
    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")
