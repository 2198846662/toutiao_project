from datetime import datetime
from sqlalchemy import DateTime, Index, Integer, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class  History(Base):
    __tablename__ = "history"

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news_history"),  #确保同一用户对同一新闻只能有一个浏览记录
        Index("idx_user_id_history", "user_id"),  #为 user_id 字段创建索引
        Index("idx_news_id_history", "news_id"),  #为 news_id 字段创建索引
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="浏览记录ID")
    user_id : Mapped[int] = mapped_column(Integer, nullable=False, comment="用户ID")
    news_id : Mapped[int] = mapped_column(Integer, nullable=False, comment="新闻ID")
    view_time : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="浏览时间")

    def __repr__(self) -> str:
        return f"History(id={self.id}, user_id={self.user_id}, news_id={self.news_id})"