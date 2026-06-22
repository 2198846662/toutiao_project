from datetime import datetime
from unittest import TestCase

from models.ai import AIChatSession, AIChatMessage
from routers.ai import _format_session


class AIChatContractTest(TestCase):
    def test_ai_models_match_multi_turn_tables(self):
        self.assertEqual(AIChatSession.__tablename__, "ai_chat_session")
        self.assertEqual(AIChatMessage.__tablename__, "ai_chat_message")

        session_columns = set(AIChatSession.__table__.columns.keys())
        message_columns = set(AIChatMessage.__table__.columns.keys())

        self.assertEqual(
            session_columns,
            {"id", "session_id", "user_id", "title", "summary", "created_at", "updated_at"},
        )
        self.assertEqual(message_columns, {"id", "session_id", "user_id", "role", "content", "created_at"})

    def test_format_session_returns_frontend_session_shape(self):
        session = AIChatSession(
            id=7,
            session_id="session-abc",
            user_id=3,
            title="Python学习",
            summary="聊 Python",
            created_at=datetime(2026, 6, 22, 12, 0, 0),
            updated_at=datetime(2026, 6, 22, 12, 3, 0),
        )

        data = _format_session(session)

        self.assertEqual(data["session_id"], "session-abc")
        self.assertEqual(data["title"], "Python学习")
        self.assertEqual(data["summary"], "聊 Python")
        self.assertEqual(data["created_at"], session.created_at)
        self.assertEqual(data["updated_at"], session.updated_at)
