from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminNewsRequest(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=500)
    content: str
    image: str | None = Field(None, max_length=255)
    author: str | None = Field(None, max_length=100)
    category_id: int = Field(..., alias="categoryId")
    views: int = Field(0, ge=0)
    publish_time: datetime | None = Field(None, alias="publishTime")

    model_config = ConfigDict(populate_by_name=True)


class AdminCategoryRequest(BaseModel):
    name: str = Field(..., max_length=50)
    sort_order: int = Field(0, alias="sortOrder")

    model_config = ConfigDict(populate_by_name=True)


class AdminNewsResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    content: str
    image: str | None = None
    author: str | None = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: datetime | None = Field(None, alias="publishTime")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminCategoryResponse(BaseModel):
    id: int
    name: str
    sort_order: int = Field(alias="sortOrder")
    created_at: datetime | None = Field(None, alias="createdAt")
    updated_at: datetime | None = Field(None, alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str | None = None
    phone: str | None = None
    role: str
    created_at: datetime | None = Field(None, alias="createdAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
