from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AIChatSession(Base):
    __tablename__ = "ai_chat_session"

    __table_args__ = (
        Index("idx_ai_chat_session_user_id", "user_id"),
        Index("idx_ai_chat_session_updated_at", "updated_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="会话ID")
    session_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="公开会话ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    title: Mapped[str | None] = mapped_column(String(100), nullable=True, comment="会话标题")
    summary: Mapped[str | None] = mapped_column(String(255), nullable=True, comment="会话摘要")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        comment="更新时间",
    )


class AIChatMessage(Base):
    __tablename__ = "ai_chat_message"

    __table_args__ = (
        Index("idx_ai_chat_message_session_id", "session_id"),
        Index("idx_ai_chat_message_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="消息ID")
    session_id: Mapped[str] = mapped_column(String(64), nullable=False, comment="公开会话ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    role: Mapped[str] = mapped_column(String(20), nullable=False, comment="消息角色：user/assistant/system")
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="消息内容")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
