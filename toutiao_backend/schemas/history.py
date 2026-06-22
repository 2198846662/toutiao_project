from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase

class HistoryAddRequest(BaseModel):
    news_id: int = Field(..., description="新闻ID", alias="newsId")


class HistoryNewsItemResponse(NewsItemBase):
    history_id: int = Field(..., alias="historyId", description="浏览记录ID")
    view_time: datetime = Field(..., alias="viewTime", description="浏览时间")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )


class HistoryListResponse(BaseModel):
    list: list[HistoryNewsItemResponse]
    total: int = Field(..., description="浏览记录总数")
    has_more: bool = Field(..., alias="hasMore", description="是否有更多数据")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
    )
    
