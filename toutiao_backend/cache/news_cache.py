#新闻相关的缓存方法
#key - value
from typing import Any, Dict, List

from config.cache_conf import delete_cache_pattern, get_cache_json, set_cache


CATEGORIES_KEY_PREFIX = "news_cache:categories"    # key名前缀
NEWS_LIST_KEY_PREFIX = "news_list:"   # 新闻列表缓存 key 前缀
NEWS_DETAIL_KEY_PREFIX = "news_detail:"
RELATED_NEWS_KEY_PREFIX = "related_news:"


#获取新闻分类缓存
async def get_cached_categories(skip: int = 0, limit: int = 10):
    key = f"{CATEGORIES_KEY_PREFIX}:{skip}:{limit}"
    return await get_cache_json(key)
    


#写入新闻分类缓存：缓存的数据 + 过期时间（秒）
#分类、配置：7200；列表：600；详情：1800；验证码：120 ————数据越稳定，缓存时间越久
async def set_cached_categories(data: List[Dict[str, Any]], skip: int = 0, limit: int = 10, expire=7200):
    key = f"{CATEGORIES_KEY_PREFIX}:{skip}:{limit}"
    return await set_cache(key, data, expire)


#写入缓存(新闻列表) key = news_list：分类id：页码：每页数量 + value(列表数据) + 过期时间
async def set_cache_new_list(category_id: int | None, page:int, size: int, news_list: List[Dict[str, Any]], expire=1800):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key, news_list, expire)

#获取新闻列表缓存
async def get_cache_news_list(category_id: int | None, page:int, size: int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_KEY_PREFIX}{category_part}:{page}:{size}"
    return await get_cache_json(key)


# 写入新闻详情缓存
async def set_cached_news_detail(news_id: int, news_detail: Dict[str, Any], expire=1800):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await set_cache(key, news_detail, expire)


# 获取新闻详情缓存
async def get_cached_news_detail(news_id: int):
    key = f"{NEWS_DETAIL_KEY_PREFIX}{news_id}"
    return await get_cache_json(key)


# 写入相关推荐缓存
async def set_cached_related_news(news_id: int, category_id: int, limit: int, related_news: List[Dict[str, Any]], expire=1800):
    key = f"{RELATED_NEWS_KEY_PREFIX}{news_id}:{category_id}:{limit}"
    return await set_cache(key, related_news, expire)


# 获取相关推荐缓存
async def get_cached_related_news(news_id: int, category_id: int, limit: int):
    key = f"{RELATED_NEWS_KEY_PREFIX}{news_id}:{category_id}:{limit}"
    return await get_cache_json(key)


async def clear_news_cache():
    await delete_cache_pattern(f"{CATEGORIES_KEY_PREFIX}:*")
    await delete_cache_pattern(f"{NEWS_LIST_KEY_PREFIX}*")
    await delete_cache_pattern(f"{NEWS_DETAIL_KEY_PREFIX}*")
    await delete_cache_pattern(f"{RELATED_NEWS_KEY_PREFIX}*")
