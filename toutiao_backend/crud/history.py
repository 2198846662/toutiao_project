from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.history import History
from models.news import News


#检查用户是否浏览过，如果浏览过就更新时间，否则添加浏览记录
async def add_history(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    #查询是否有浏览记录
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    history = result.scalar_one_or_none()

    if history:
        #如果有浏览记录，更新浏览时间
        history.view_time = func.now()
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history
    else:
        #如果没有浏览记录，添加新的记录
        new_history = History(user_id=user_id, news_id=news_id)
        db.add(new_history)
        await db.commit()
        await db.refresh(new_history)
        return new_history


# 获取浏览记录列表
async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int = 1,
        page_size: int = 10
):
    count_query = select(func.count()).where(History.user_id == user_id)
    total_result = await db.execute(count_query)
    total_count = total_result.scalar_one()

    query = (
        select(
            News,
            History.id.label("history_id"),
            History.view_time.label("view_time")
        )
        .join(History, News.id == History.news_id)
        .where(History.user_id == user_id)
        .order_by(History.view_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return result.all(), total_count


# 删除单条浏览记录
async def remove_history_by_id(
        db: AsyncSession,
        user_id: int,
        history_id: int
):
    query = select(History).where(
        History.id == history_id,
        History.user_id == user_id
    )
    result = await db.execute(query)
    history = result.scalar_one_or_none()
    if not history:
        return False

    await db.delete(history)
    await db.commit()
    return True


# 清空浏览记录
async def remove_all_history(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0
