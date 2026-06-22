from datetime import datetime
from sqlalchemy import DateTime, Index, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

    
class Favorite(Base):
    __tablename__ = "favorite"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news"),  #确保同一用户对同一新闻只能有一个收藏记录
        Index("idx_user_id", "user_id"),  #为 user_id 字段创建索引
        Index("idx_news_id", "news_id"),  #为 news_id 字段创建索引
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="收藏ID")
    user_id : Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    news_id : Mapped[int] = mapped_column(Integer, nullable=False, comment="新闻ID")
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="收藏时间")

    def __repr__(self) -> str:
        return f"Favorite(id={self.id}, user_id={self.user_id}, news_id={self.news_id})"
