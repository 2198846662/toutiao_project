from fastapi  import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from crud.favorite import add_news_favorite, is_new_favorite, remove_all_favorite, remove_news_favorite
from models.users import User
from schemas.favorite import FavoriteAddRequest, FavoriteCheckResponse, FavoriteListResponse
from untils.auth import get_current_user
from untils.response import success_response
from crud.favorite import get_favorite_list

router = APIRouter(prefix="/api/favorite", tags=["favorite"])

@router.get("/check")
async def check_favorite(
    news_id: int = Query(..., description="新闻ID", alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_favorite = await is_new_favorite(db, user.id, news_id)

    return success_response(message="检查收藏状态成功",data=FavoriteCheckResponse(isFavorite=is_favorite))

#添加收藏
@router.post("/add")
async def add_favorite(
    data: FavoriteAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    is_favorite = await is_new_favorite(db, user.id, data.news_id)
    if is_favorite:
        return success_response(
            message="已收藏，无需重复添加",
            data={"newsId": data.news_id, "isFavorite": True},
        )

    await add_news_favorite(db, user.id, data.news_id)
    return success_response(
        message="添加收藏成功",
        data={"newsId": data.news_id, "isFavorite": True},
    )

#删除收藏
@router.delete("/remove")
async def remove_favorite(
    news_id: int = Query(..., description="新闻ID", alias="newsId"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    remove_favorite = await remove_news_favorite(db, user.id, news_id)
    if remove_favorite:
        return success_response(
            message="删除收藏成功",
            data={"newsId": news_id, "isFavorite": False},
        )
    return success_response(
        message="收藏记录不存在",
        data={"newsId": news_id, "isFavorite": False},
    )
        

#收藏列表
@router.get("/list")
async def get_favorite_lists(
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
): 
    favorites, total_count = await get_favorite_list(db, user.id, page, page_size)
    favorites_list = [{
        **news.__dict__,
        "favorite_time": favorite_time,
        "favorite_id": favorite_id
    } for news, favorite_time, favorite_id in favorites]
    has_more = (page * page_size) < total_count

    data = FavoriteListResponse(
        list=favorites_list,
        total=total_count,
        hasMore=has_more
    )
    return success_response(message="获取收藏列表成功", data=data)


#清除收藏列表
@router.delete("/clear")
async def clear_favorite(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await remove_all_favorite(db, user.id)
    return success_response(message=f"删除{count}个收藏成功")