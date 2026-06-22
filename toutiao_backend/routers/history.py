from fastapi  import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from untils.auth import get_current_user
from untils.response import success_response
from crud.history import add_history, get_history_list, remove_all_history, remove_history_by_id

router = APIRouter(prefix="/api/history", tags=["history"])

#添加浏览记录
@router.post("/add")
async def add_history1(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    history = await add_history(db, user.id, data.news_id)
    return success_response(
        message="添加浏览记录成功",
        data={"newsId": data.news_id, "historyId": history.id},
    )

# 获取浏览记录列表(分页功能)
@router.get("/list")
async def get_history_list1(
    page: int = Query(1, description="页码", ge=1),
    page_size: int = Query(10, description="每页数量", ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    rows, total_count = await get_history_list(db, user.id, page, page_size)
    history_list = [
        {
            **news.__dict__,
            "history_id": history_id,
            "view_time": view_time,
        }
        for news, history_id, view_time in rows
    ]
    has_more = (page * page_size) < total_count
    data = HistoryListResponse(
        list=history_list,
        total=total_count,
        hasMore=has_more,
    )
    return success_response(message="获取浏览记录列表成功", data=data)

#删除单条浏览记录
@router.delete("/delete/{history_id}")
async def remove_history(
    history_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    removed = await remove_history_by_id(db, user.id, history_id)
    if removed:
        return success_response(
            message="删除浏览记录成功",
            data={"historyId": history_id},
        )
    return success_response(
        message="浏览记录不存在",
        data={"historyId": history_id},
    )


#清空浏览记录
@router.delete("/clear")
async def clear_history(        
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await remove_all_history(db, user.id)
    return success_response(
        message=f"删除{count}条浏览记录成功",
        data={"count": count},
    )
