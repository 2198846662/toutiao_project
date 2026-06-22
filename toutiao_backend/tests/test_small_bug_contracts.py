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
