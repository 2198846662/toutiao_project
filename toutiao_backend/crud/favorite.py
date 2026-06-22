from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News
async def is_new_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
        ) -> bool:
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()
    return favorite is not None

#添加收藏
async def add_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

#删除收藏
async def remove_news_favorite(
    db: AsyncSession,
    user_id: int,
    news_id: int
):
    query = select(Favorite).where(Favorite.user_id == user_id, Favorite.news_id == news_id)
    result = await db.execute(query)
    favorite = result.scalar_one_or_none()
    if favorite:
        await db.delete(favorite)
        await db.commit()
        return True
    return False

#获取收藏列表(获取的是某个用户的收藏列表 + 分页功能)
async def get_favorite_list(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    page_size: int = 10
):
    #总量 + 收藏的新闻列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    total = await db.execute(count_query)
    total_count = total.scalar_one()

    #获取列表 + 联表查询join() + 收藏时间排序 + 分页
    select_query = select(News, Favorite.created_at.label("favorite_time"),Favorite.id.label("favorite_id")).join(Favorite, News.id == Favorite.news_id).where(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(select_query)
    favorites = result.all()
    return favorites, total_count

#清除收藏列表
async def remove_all_favorite(
    db: AsyncSession,
    user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    #返回一个删除的数量
    return result.rowcount or 0