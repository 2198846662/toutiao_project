from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, patch

from crud import news_cache
from models.news import Category, News


class FakeScalarResult:
    def __init__(self, rows):
        self._rows = rows

    def all(self):
        return self._rows

    def one_or_none(self):
        return self._rows[0] if self._rows else None


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return FakeScalarResult(self._rows)

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None


class FakeDb:
    def __init__(self, rows):
        self.rows = rows
        self.execute = AsyncMock(return_value=FakeResult(rows))


class FailingDb:
    async def execute(self, stmt):
        raise AssertionError("database should not be queried on cache hit")


class NewsCacheTest(IsolatedAsyncioTestCase):
    async def test_categories_return_from_cache_without_querying_database(self):
        cached = [{"id": 1, "name": "头条", "sort_order": 0}]

        with patch("crud.news_cache.get_cached_categories", new=AsyncMock(return_value=cached)):
            categories = await news_cache.get_categories(FailingDb(), skip=0, limit=10)

        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0].id, 1)
        self.assertEqual(categories[0].name, "头条")

    async def test_categories_cache_miss_queries_database_and_writes_page_cache(self):
        db = FakeDb([Category(id=2, name="社会", sort_order=1)])

        with (
            patch("crud.news_cache.get_cached_categories", new=AsyncMock(return_value=None)),
            patch("crud.news_cache.set_cached_categories", new=AsyncMock(return_value=True)) as set_cache,
        ):
            categories = await news_cache.get_categories(db, skip=0, limit=10)

        self.assertEqual(categories[0].id, 2)
        db.execute.assert_awaited_once()
        set_cache.assert_awaited_once()
        self.assertEqual(set_cache.await_args.args[1], 0)
        self.assertEqual(set_cache.await_args.args[2], 10)

    async def test_news_list_return_from_cache_without_querying_database(self):
        cached = [{
            "id": 1,
            "title": "缓存新闻",
            "description": "简介",
            "content": "内容",
            "image": None,
            "author": "作者",
            "category_id": 1,
            "views": 3,
        }]

        with patch("crud.news_cache.get_cache_news_list", new=AsyncMock(return_value=cached)):
            news_list = await news_cache.get_news_list(FailingDb(), category_id=1, skip=0, limit=10)

        self.assertEqual(len(news_list), 1)
        self.assertEqual(news_list[0].title, "缓存新闻")

    async def test_news_list_cache_miss_returns_database_rows_and_caches_empty_list(self):
        db = FakeDb([])

        with (
            patch("crud.news_cache.get_cache_news_list", new=AsyncMock(return_value=None)),
            patch("crud.news_cache.set_cache_new_list", new=AsyncMock(return_value=True)) as set_cache,
        ):
            news_list = await news_cache.get_news_list(db, category_id=1, skip=0, limit=10)

        self.assertEqual(news_list, [])
        db.execute.assert_awaited_once()
        set_cache.assert_awaited_once_with(1, 1, 10, [])

    async def test_news_detail_return_from_cache_without_querying_database(self):
        cached = {
            "id": 4,
            "title": "缓存详情",
            "description": "简介",
            "content": "内容",
            "image": None,
            "author": "作者",
            "category_id": 1,
            "views": 8,
        }

        with patch("crud.news_cache.get_cached_news_detail", new=AsyncMock(return_value=cached)):
            detail = await news_cache.get_news_detail(FailingDb(), news_id=4)

        self.assertEqual(detail.id, 4)
        self.assertEqual(detail.title, "缓存详情")

    async def test_news_detail_cache_miss_queries_database_and_writes_cache(self):
        db = FakeDb([News(
            id=5,
            title="数据库详情",
            description="简介",
            content="内容",
            image=None,
            author="作者",
            category_id=1,
            views=9,
        )])

        with (
            patch("crud.news_cache.get_cached_news_detail", new=AsyncMock(return_value=None)),
            patch("crud.news_cache.set_cached_news_detail", new=AsyncMock(return_value=True)) as set_cache,
        ):
            detail = await news_cache.get_news_detail(db, news_id=5)

        self.assertEqual(detail.id, 5)
        db.execute.assert_awaited_once()
        set_cache.assert_awaited_once()
        self.assertEqual(set_cache.await_args.args[0], 5)

    async def test_related_news_return_from_cache_without_querying_database(self):
        cached = [{
            "id": 6,
            "title": "缓存推荐",
            "content": "内容",
            "views": 7,
            "image": None,
            "author": "作者",
            "publishTime": "2026-01-01T00:00:00",
            "categoryId": 1,
        }]

        with patch("crud.news_cache.get_cached_related_news", new=AsyncMock(return_value=cached)):
            related = await news_cache.get_related_news(FailingDb(), news_id=4, category_id=1)

        self.assertEqual(related, cached)

    async def test_related_news_cache_miss_queries_database_and_caches_empty_list(self):
        db = FakeDb([])

        with (
            patch("crud.news_cache.get_cached_related_news", new=AsyncMock(return_value=None)),
            patch("crud.news_cache.set_cached_related_news", new=AsyncMock(return_value=True)) as set_cache,
        ):
            related = await news_cache.get_related_news(db, news_id=4, category_id=1, limit=5)

        self.assertEqual(related, [])
        db.execute.assert_awaited_once()
        set_cache.assert_awaited_once_with(4, 1, 5, [])
