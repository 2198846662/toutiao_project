from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase

class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite", description="是否收藏")


class FavoriteAddRequest(BaseModel):
    news_id: int = Field(..., alias="newsId", description="新闻ID")


#规划两个类：一个是新闻模型类，一个是收藏模型类
class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id: int = Field(alias="favoriteId", description="收藏ID")
    favorite_time: str = Field(alias="favoriteTime", description="收藏时间")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
        )


#收藏列表响应类
class FavoriteListResponse(BaseModel):
    list: list[FavoriteNewsItemResponse]
    total: int = Field(..., description="收藏总数")
    has_more: bool = Field(alias="hasMore", description="是否有更多数据")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True
        )