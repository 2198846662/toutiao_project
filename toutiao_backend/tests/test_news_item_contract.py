from datetime import datetime
from types import SimpleNamespace
from unittest import TestCase

from schemas.history import HistoryNewsItemResponse
from schemas.base import NewsItemBase


def make_news_item():
    return SimpleNamespace(
        id=1,
        title="测试新闻",
        description="简介",
        image=None,
        author="作者",
        category_id=2,
        views=10,
        publish_time=datetime(2026, 1, 2, 3, 4, 5),
    )


class NewsItemContractTest(TestCase):
    def test_news_item_schema_uses_frontend_publish_time_alias(self):
        payload = NewsItemBase.model_validate(make_news_item()).model_dump(by_alias=True)

        self.assertIn("publishTime", payload)
        self.assertNotIn("publishedTime", payload)
        self.assertEqual(payload["categoryId"], 2)

    def test_history_item_response_reuses_news_item_base_contract(self):
        payload = HistoryNewsItemResponse.model_validate({
            **make_news_item().__dict__,
            "history_id": 3,
            "view_time": datetime(2026, 1, 3, 4, 5, 6),
        }).model_dump(by_alias=True)

        self.assertTrue(issubclass(HistoryNewsItemResponse, NewsItemBase))
        self.assertIn("publishTime", payload)
        self.assertIn("categoryId", payload)
        self.assertEqual(payload["historyId"], 3)
        self.assertEqual(payload["viewTime"], datetime(2026, 1, 3, 4, 5, 6))
