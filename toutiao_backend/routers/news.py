from fastapi import APIRouter, HTTPException, Query, Depends
from crud import news
from config.db_conf import get_db
from sqlalchemy.ext.asyncio import AsyncSession
#创建 APIRouter 实例
#prefix: 路由前缀，tags: 路由标签
router = APIRouter(prefix="/api/news", tags=["news"])

#接口实现流程
#1. 模块化路由 -> API 接口规范文档
#2. 定义模型类 -> 数据库表结构
#3. 在crud文件夹里面创建文件：封装操作数据库的方法 
#4. 在路由处理函数里面调用 crud 封装好的方法，响应结果


@router.get("/categories")
async def get_news_categories(
    skip: int = Query(0, description="跳过的记录数"),
    limit: int = Query(10, description="返回的记录数"),
    db: AsyncSession = Depends(get_db)
    ):
    #先获取数据库里面的新闻分类数据 -> 先定义模型类  -> 封装查询数据的方法
    categories = await news.get_categories(db, skip, limit)  #调用crud封装好的方法，获取数据
    return {
        "code": 200,
        "msg": "获取新闻分类成功",
        "data": categories
    }

@router.get("/list")
async def get_news_list(
    category_id: int = Query(..., description="新闻分类ID",alias="categoryId"),
    page: int = Query(1, description="页码"), 
    page_size: int = Query(10, description="每页记录数", alias="pageSize", le=100),
    db: AsyncSession = Depends(get_db)
    ):
    # 思路：处理分页规则 -> 查询新闻列表 -> 计算总量 -> 计算是否有更多数据
    skip = (page - 1) * page_size
    limit = page_size
    news_list = await news.get_news_list(db, category_id, skip, limit)  #调用crud封装好的方法，获取数据
    total = await news.get_news_count(db, category_id)  #查询总量
    #跳过的+当前的数量 < 总量 说明还有更多数据
    has_more =skip + len(news_list) < total
    return {
        "code": 200,
        "msg": "获取新闻列表成功",
        "data": {
            "list": news_list,
            "total": total,  #这里返回查询到的总量
            "hasMore": has_more  #这里可以根据实际情况计算是否有更多数据,
        }
    }

@router.get("/detail")
async def get_news_detail(
    news_id: int = Query(..., description="新闻ID", alias="id"),
    db: AsyncSession = Depends(get_db)
    ):
    #获取新闻详情 + 浏览量+1 + 相关新闻
    news_detail = await news.get_news_detail(db, news_id)  #调用crud封装好的方法，获取数据
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻未找到")
    
    views_res = await news.increase_news_views(db, news_detail.id)  #增加浏览量
    if not views_res:
        raise HTTPException(status_code=500, detail="增加浏览量失败")        
    
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)  #查询相关新闻

    return {
        "code": 200,
        "msg": "获取新闻详情成功",
        "data": {
            "id": news_detail.id,  
            "title": news_detail.title,
            "content": news_detail.content, 
            "views": news_detail.views,
            "image": news_detail.image,
            "author": news_detail.author,
            "publishTime": news_detail.publish_time,
            "categoryId": news_detail.category_id,
            "relatedNews": related_news
        }
    }


           
