from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cache.news_cache import (
    get_cache_news_list,
    get_cached_categories,
    get_cached_news_detail,
    get_cached_related_news,
    set_cache_new_list,
    set_cached_categories,
    set_cached_news_detail,
    set_cached_related_news,
)
from models.news import Category, News

#查缓存 -> 没有缓存 -> 查数据库 -> 更新缓存
async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    #尝试从缓存中获取数据
    cached_categories = await get_cached_categories(skip, limit)   #数据缓存json
    #把json格式转成orm对象
    if cached_categories is not None:
        return [Category(**item) for item in cached_categories]
    
    #查数据库
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories =  result.scalars().all()    #ORM

    #写入缓存，空列表也缓存，避免反复查库
    await set_cached_categories(jsonable_encoder(categories), skip, limit)

    #返回数据
    return categories


async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    if limit <= 0:
        raise ValueError("limit必须大于0")

    #尝试缓存中获取数据
    cached_news_list = await get_cache_news_list(category_id, skip // limit + 1, limit)     #数据缓存json
    #把json格式转成orm对象(列表推导式)
    if cached_news_list is not None:
        return [News(**item) for item in cached_news_list]  
    

    # 查询新闻分类下的新闻列表
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    #写入缓存，空列表也缓存，避免反复查库
    await set_cache_new_list(category_id, skip // limit + 1, limit, jsonable_encoder(news_list))
    return news_list


async def get_news_count(db: AsyncSession, category_id: int):
    #查询指定分类下的新闻数量
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_news_detail(db: AsyncSession, news_id: int):
    cached_news_detail = await get_cached_news_detail(news_id)
    if cached_news_detail is not None:
        return News(**cached_news_detail)

    stmt = select(News).where(News.id == news_id)
    result = await db.execute(stmt)
    news_detail = result.scalar_one_or_none()
    if news_detail:
        await set_cached_news_detail(news_id, jsonable_encoder(news_detail))
    return news_detail


async def set_news_detail_cache(news_detail: News):
    return await set_cached_news_detail(news_detail.id, jsonable_encoder(news_detail))

async def increase_news_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(News.id == news_id).values(views=News.views + 1)
    result = await db.execute(stmt)
    await db.commit()
    # 检查数据库是否命中    命中 -> 返回True
    if result.rowcount > 0:
        return True
    return False
    
async def get_related_news(db: AsyncSession, news_id: int, category_id: int, limit: int = 5):
    cached_related_news = await get_cached_related_news(news_id, category_id, limit)
    if cached_related_news is not None:
        return cached_related_news

    #order_by排序 -> 浏览量和发布时间
    stmt = select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),      #desc() 降序  asc() 升序
        News.publish_time.desc()       
        ).limit(limit)
    result = await db.execute(stmt)
    # return result.scalars().all()
    related_news = result.scalars().all()
    #列表推导式中推导出新闻的核心数据，然后return
    related_news_list = [{
       "id": news_detail.id,  
        "title": news_detail.title,
        "content": news_detail.content, 
        "views": news_detail.views,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
    } for news_detail in related_news]

    await set_cached_related_news(news_id, category_id, limit, jsonable_encoder(related_news_list))
    return related_news_list
