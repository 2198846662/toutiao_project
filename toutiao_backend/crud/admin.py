from datetime import datetime

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.history import History
from models.news import Category, News
from models.users import User
from schemas.admin import AdminCategoryRequest, AdminNewsRequest


async def get_dashboard_stats(db: AsyncSession):
    queries = {
        "userCount": select(func.count(User.id)),
        "newsCount": select(func.count(News.id)),
        "categoryCount": select(func.count(Category.id)),
        "favoriteCount": select(func.count(Favorite.id)),
        "historyCount": select(func.count(History.id)),
    }
    data = {}
    for key, stmt in queries.items():
        result = await db.execute(stmt)
        data[key] = result.scalar_one()
    return data


async def get_news_list(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category_id: int | None = None,
):
    stmt = select(News)
    count_stmt = select(func.count(News.id))

    conditions = []
    if keyword:
        pattern = f"%{keyword}%"
        conditions.append(or_(News.title.like(pattern), News.description.like(pattern), News.author.like(pattern)))
    if category_id:
        conditions.append(News.category_id == category_id)

    for condition in conditions:
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()

    result = await db.execute(
        stmt.order_by(News.publish_time.desc(), News.id.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    return result.scalars().all(), total


async def create_news(db: AsyncSession, data: AdminNewsRequest):
    news = News(**data.model_dump(by_alias=False, exclude_none=True))
    if news.publish_time is None:
        news.publish_time = datetime.now()
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def update_news(db: AsyncSession, news_id: int, data: AdminNewsRequest):
    news = await db.get(News, news_id)
    if not news:
        return None

    for key, value in data.model_dump(by_alias=False, exclude_none=True).items():
        setattr(news, key, value)
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news


async def delete_news(db: AsyncSession, news_id: int):
    result = await db.execute(delete(News).where(News.id == news_id))
    await db.commit()
    return result.rowcount > 0


async def get_categories(db: AsyncSession):
    result = await db.execute(select(Category).order_by(Category.sort_order.asc(), Category.id.asc()))
    return result.scalars().all()


async def create_category(db: AsyncSession, data: AdminCategoryRequest):
    category = Category(**data.model_dump(by_alias=False))
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, category_id: int, data: AdminCategoryRequest):
    category = await db.get(Category, category_id)
    if not category:
        return None

    for key, value in data.model_dump(by_alias=False).items():
        setattr(category, key, value)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int):
    result = await db.execute(delete(Category).where(Category.id == category_id))
    await db.commit()
    return result.rowcount > 0


async def get_users(db: AsyncSession, page: int = 1, page_size: int = 10, keyword: str | None = None):
    stmt = select(User)
    count_stmt = select(func.count(User.id))
    if keyword:
        pattern = f"%{keyword}%"
        condition = or_(User.username.like(pattern), User.nickname.like(pattern), User.phone.like(pattern))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    result = await db.execute(stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size))
    return result.scalars().all(), total
