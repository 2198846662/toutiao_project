from pathlib import Path
from unittest import TestCase

from models.news import News


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SmallBugContractsTest(TestCase):
    def test_news_repr_uses_existing_views_field(self):
        news = News(id=1, title="测试新闻", views=8)

        self.assertIn("views=8", repr(news))

    def test_profile_uses_vant4_toast_functions(self):
        profile = (PROJECT_ROOT / "toutiao_frontend/src/views/Profile.vue").read_text(encoding="utf-8")

        self.assertNotIn("showToast.clear", profile)
        self.assertNotIn("showToast.fail", profile)
        self.assertIn("closeToast", profile)
        self.assertIn("showFailToast", profile)

    def test_history_local_delete_can_fallback_to_news_id(self):
        history_view = (PROJECT_ROOT / "toutiao_frontend/src/views/History.vue").read_text(encoding="utf-8")
        history_store = (PROJECT_ROOT / "toutiao_frontend/src/store/modules/history.js").read_text(encoding="utf-8")

        self.assertIn("confirmDelete(item.historyId || item.id)", history_view)
        self.assertIn("item.historyId ? item.historyId !== historyId : item.id !== historyId", history_store)

    def test_user_crud_uses_value_error_for_business_failures(self):
        users_crud = (PROJECT_ROOT / "toutiao_backend/crud/users.py").read_text(encoding="utf-8")

        self.assertNotIn("raise Exception", users_crud)
        self.assertIn("raise ValueError", users_crud)

    def test_admin_route_guard_uses_pinia_store_and_login_redirect(self):
        router = (PROJECT_ROOT / "toutiao_frontend/src/router/index.js").read_text(encoding="utf-8")
        login = (PROJECT_ROOT / "toutiao_frontend/src/views/Login.vue").read_text(encoding="utf-8")

        self.assertIn("useUserStore", router)
        self.assertIn("getAuthToken", router)
        self.assertIn("query: { redirect: to.fullPath }", router)
        self.assertIn("useRoute", login)
        self.assertIn("route.query.redirect", login)

    def test_ai_chat_local_state_is_scoped_to_current_user(self):
        chat_store = (PROJECT_ROOT / "toutiao_frontend/src/store/modules/chat.js").read_text(encoding="utf-8")
        ai_chat = (PROJECT_ROOT / "toutiao_frontend/src/views/AIChat.vue").read_text(encoding="utf-8")

        self.assertIn("ownerKey", chat_store)
        self.assertIn("getPersistedUserStore", chat_store)
        self.assertIn("getCurrentOwnerKey", chat_store)
        self.assertIn("ensureCurrentUser", chat_store)
        self.assertIn("chatStore.ensureCurrentUser()", ai_chat)
        self.assertIn("const sessionId = chatStore.currentSessionId || chatStore.sessions[0]?.session_id", ai_chat)
