from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    __table_args__ = (
        Index("idx_username", "username"),  #为 username 字段创建索引
        Index("idx_phone", "phone")  #为 phone 字段创建索引
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="用户ID")
    username : Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="用户名")
    password : Mapped[str] = mapped_column(String(255), nullable=False, comment="用户密码")
    nickname : Mapped[str|None] = mapped_column(String(50), comment="用户昵称")
    avatar : Mapped[str|None] = mapped_column(String(255), comment="用户头像URL")
    gender : Mapped[str|None] = mapped_column(Enum('male', 'female', 'unknown'), comment="用户性别",default='unknown')
    bio : Mapped[str|None] = mapped_column(String(500), comment="用户简介",default="这个人很懒...")
    phone : Mapped[str|None] = mapped_column(String(20), unique=True, comment="用户手机号")
    role : Mapped[str] = mapped_column(String(20), default="user", nullable=False, comment="用户角色")
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")
    updated_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


    def __repr__(self) -> str:
        return f"User(id={self.id}, username='{self.username}')"
    

class UserToken(Base):
    __tablename__ = "user_token"

    __table_args__ = (
        Index("idx_user_id", "user_id"),  #为 user_id 字段创建索引
        Index("idx_token", "token")  #为 token 字段创建索引
    )

    id : Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="ID")
    user_id : Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False, comment="用户ID")
    token : Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="访问令牌")
    expires_at : Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="令牌过期时间")
    created_at : Mapped[datetime] = mapped_column(DateTime, default=datetime.now, comment="创建时间")

    def __repr__(self) -> str:
        return f"UserToken(id={self.id}, user_id={self.user_id})"
