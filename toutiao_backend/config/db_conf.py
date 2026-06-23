
import os
from pathlib import Path

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()

#数据库url，真实账号密码请写入本地 .env，不要提交到仓库
DATABASE_URL = os.getenv("DATABASE_URL") or URL.create(
    "mysql+aiomysql",
    username=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "news_app"),
    query={"charset": "utf8mb4"},
)

#创建异步引擎
engine = create_async_engine(
    DATABASE_URL, 
    echo=True,
    pool_size=10,  #连接池大小
    max_overflow=20,  #连接池最大溢出数量
    )


#创建异步会话工厂
async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,  #提交后不失效
    class_=AsyncSession  #使用异步会话类 
    )

#依赖项，用于获取异步会话
async def get_db() -> AsyncSession: # type: ignore
    async with async_session_factory() as session:
        yield session





