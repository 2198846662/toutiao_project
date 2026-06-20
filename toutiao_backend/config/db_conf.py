
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

#数据库url
DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"

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





