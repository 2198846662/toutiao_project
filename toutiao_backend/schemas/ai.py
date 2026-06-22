from typing import Literal

from pydantic import BaseModel, Field


class AIMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class AIChatRequest(BaseModel):
    model: str | None = None
    messages: list[AIMessage] = Field(default_factory=list)
    stream: bool = True
    session_id: str | None = None


class AIChatSessionResponse(BaseModel):
    session_id: str
    title: str | None = None
    summary: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class AIChatMessagesResponse(BaseModel):
    session_id: str
    messages: list[AIMessage]
