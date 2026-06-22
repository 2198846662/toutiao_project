from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import get_db
from cache.news_cache import clear_news_cache
from crud import admin as admin_crud
from models.users import User
from schemas.admin import AdminCategoryRequest, AdminCategoryResponse, AdminNewsRequest, AdminNewsResponse, AdminUserResponse
from untils.auth import get_current_user
from untils.response import success_response


router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(user: User = Depends(get_current_user)):
    if getattr(user, "role", "user") != "admin":
        raise HTTPException(status_code=403, detail="无管理员权限")
    return user


@router.get("/dashboard")
async def get_dashboard(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    data = await admin_crud.get_dashboard_stats(db)
    return success_response(message="获取后台统计成功", data=data)


@router.get("/news/list")
async def get_admin_news_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100),
    keyword: str | None = Query(None),
    category_id: int | None = Query(None, alias="categoryId"),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    news_list, total = await admin_crud.get_news_list(db, page, page_size, keyword, category_id)
    items = [AdminNewsResponse.model_validate(item).model_dump(by_alias=True) for item in news_list]
    return success_response(
        message="获取新闻管理列表成功",
        data={"list": items, "total": total},
    )


@router.post("/news/add")
async def add_admin_news(
    data: AdminNewsRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    news = await admin_crud.create_news(db, data)
    await clear_news_cache()
    return success_response(message="新增新闻成功", data=AdminNewsResponse.model_validate(news).model_dump(by_alias=True))


@router.put("/news/update/{news_id}")
async def update_admin_news(
    data: AdminNewsRequest,
    news_id: int = Path(..., ge=1),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    news = await admin_crud.update_news(db, news_id, data)
    if not news:
        raise HTTPException(status_code=404, detail="新闻不存在")
    await clear_news_cache()
    return success_response(message="更新新闻成功", data=AdminNewsResponse.model_validate(news).model_dump(by_alias=True))


@router.delete("/news/delete/{news_id}")
async def delete_admin_news(
    news_id: int = Path(..., ge=1),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await admin_crud.delete_news(db, news_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="新闻不存在")
    await clear_news_cache()
    return success_response(message="删除新闻成功", data=True)


@router.get("/category/list")
async def get_admin_categories(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    categories = await admin_crud.get_categories(db)
    data = [AdminCategoryResponse.model_validate(item).model_dump(by_alias=True) for item in categories]
    return success_response(message="获取分类管理列表成功", data=data)


@router.post("/category/add")
async def add_admin_category(
    data: AdminCategoryRequest,
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    category = await admin_crud.create_category(db, data)
    await clear_news_cache()
    return success_response(
        message="新增分类成功",
        data=AdminCategoryResponse.model_validate(category).model_dump(by_alias=True),
    )


@router.put("/category/update/{category_id}")
async def update_admin_category(
    data: AdminCategoryRequest,
    category_id: int = Path(..., ge=1),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    category = await admin_crud.update_category(db, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    await clear_news_cache()
    return success_response(
        message="更新分类成功",
        data=AdminCategoryResponse.model_validate(category).model_dump(by_alias=True),
    )


@router.delete("/category/delete/{category_id}")
async def delete_admin_category(
    category_id: int = Path(..., ge=1),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    deleted = await admin_crud.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="分类不存在")
    await clear_news_cache()
    return success_response(message="删除分类成功", data=True)


@router.get("/users/list")
async def get_admin_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, alias="pageSize", ge=1, le=100),
    keyword: str | None = Query(None),
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    users, total = await admin_crud.get_users(db, page, page_size, keyword)
    items = [AdminUserResponse.model_validate(item).model_dump(by_alias=True) for item in users]
    return success_response(message="获取用户列表成功", data={"list": items, "total": total})
