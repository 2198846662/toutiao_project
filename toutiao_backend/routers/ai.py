import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from config.ai_conf import AI_API_KEY, AI_MODEL, get_chat_completions_url
from config.db_conf import get_db
from crud import ai as ai_crud
from models.users import User
from schemas.ai import AIChatRequest
from untils.auth import get_current_user
from untils.response import success_response


router = APIRouter(prefix="/api/ai", tags=["ai"])


def _format_session(session):
    title = session.title or f"会话 {session.session_id[:8]}"
    return {
        "session_id": session.session_id,
        "title": title,
        "summary": session.summary or title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


def _extract_latest_user_message(request: AIChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == "user" and message.content.strip():
            return message.content.strip()
    raise HTTPException(status_code=400, detail="消息不能为空")


def _extract_delta_content(payload: dict) -> str:
    return (
        payload.get("choices", [{}])[0].get("delta", {}).get("content")
        or payload.get("choices", [{}])[0].get("message", {}).get("content")
        or payload.get("output", {}).get("text")
        or ""
    )


@router.get("/sessions")
async def get_ai_sessions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sessions = await ai_crud.get_sessions(db, user.id)
    return success_response(message="获取AI会话列表成功", data=[_format_session(item) for item in sessions])


@router.get("/sessions/{session_id}/messages")
async def get_ai_session_messages(
    session_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    messages = await ai_crud.get_session_messages(db, user.id, session_id)
    if messages is None:
        raise HTTPException(status_code=404, detail="会话不存在")

    data = {
        "session_id": session_id,
        "messages": ai_crud.messages_to_payload(messages),
    }
    return success_response(message="获取AI会话消息成功", data=data)


@router.post("/chat")
async def chat(
    request: AIChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not AI_API_KEY:
        raise HTTPException(status_code=500, detail="AI_API_KEY未配置，请在后端.env中设置")

    user_message = _extract_latest_user_message(request)
    session = await ai_crud.get_session(db, user.id, request.session_id)
    if not session:
        session = await ai_crud.create_session(db, user.id, title=user_message[:30])

    history_messages = await ai_crud.get_session_messages(db, user.id, session.session_id) or []
    model_messages = ai_crud.messages_to_payload(history_messages)
    model_messages.append({"role": "user", "content": user_message})
    await ai_crud.create_message(db, session, "user", user_message)

    model = request.model or AI_MODEL
    payload = {
        "model": model,
        "messages": model_messages,
        "stream": request.stream,
    }

    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }

    if not request.stream:
        async with httpx.AsyncClient(timeout=60, trust_env=False) as client:
            response = await client.post(get_chat_completions_url(), headers=headers, json=payload)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        response_json = response.json()
        assistant_message = _extract_delta_content(response_json)
        if assistant_message:
            await ai_crud.create_message(db, session, "assistant", assistant_message)
        return success_response(
            message="AI回复成功",
            data={"session_id": session.session_id, "message": assistant_message},
        )

    async def event_stream():
        assistant_chunks: list[str] = []
        try:
            async with httpx.AsyncClient(timeout=None, trust_env=False) as client:
                async with client.stream("POST", get_chat_completions_url(), headers=headers, json=payload) as response:
                    if response.status_code >= 400:
                        error_text = await response.aread()
                        error_payload = {"error": {"message": error_text.decode("utf-8", errors="ignore")}}
                        yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        if not line.startswith("data: "):
                            continue

                        data = line[6:]
                        yield f"{line}\n\n"

                        if data == "[DONE]":
                            continue
                        try:
                            payload_json = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        content = _extract_delta_content(payload_json)
                        if content:
                            assistant_chunks.append(content)
        except Exception as exc:
            error_payload = {"error": {"message": f"AI服务请求失败: {exc}"}}
            yield f"data: {json.dumps(error_payload, ensure_ascii=False)}\n\n"
            return

        assistant_message = "".join(assistant_chunks)
        if assistant_message:
            await ai_crud.create_message(db, session, "assistant", assistant_message)

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"X-Session-Id": session.session_id},
    )
