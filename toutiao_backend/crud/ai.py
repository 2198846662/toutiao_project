from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_conf import engine
from models.ai import AIChatMessage, AIChatSession, Base


async def init_ai_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_session(db: AsyncSession, user_id: int, title: str | None = None):
    now = datetime.now()
    session = AIChatSession(
        session_id=uuid4().hex,
        user_id=user_id,
        title=title,
        summary=title,
        created_at=now,
        updated_at=now,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_session(db: AsyncSession, user_id: int, session_id: str | None):
    if not session_id:
        return None

    stmt = select(AIChatSession).where(AIChatSession.user_id == user_id, AIChatSession.session_id == session_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_sessions(db: AsyncSession, user_id: int, limit: int = 50):
    stmt = (
        select(AIChatSession)
        .where(AIChatSession.user_id == user_id)
        .order_by(AIChatSession.updated_at.desc(), AIChatSession.id.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_session_messages(db: AsyncSession, user_id: int, session_id: str | None):
    session = await get_session(db, user_id, session_id)
    if not session:
        return None

    stmt = (
        select(AIChatMessage)
        .where(AIChatMessage.session_id == session.session_id, AIChatMessage.user_id == user_id)
        .order_by(AIChatMessage.created_at.asc(), AIChatMessage.id.asc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def create_message(db: AsyncSession, session: AIChatSession, role: str, content: str):
    message = AIChatMessage(session_id=session.session_id, user_id=session.user_id, role=role, content=content)
    session.updated_at = datetime.now()
    db.add(message)
    db.add(session)
    await db.commit()
    await db.refresh(message)
    await db.refresh(session)
    return message


def messages_to_payload(messages: list[AIChatMessage]):
    return [{"role": item.role, "content": item.content} for item in messages]
