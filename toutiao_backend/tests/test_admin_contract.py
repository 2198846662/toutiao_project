from unittest import TestCase

from models.users import User
from routers import admin
from schemas.admin import AdminCategoryRequest, AdminNewsRequest


class AdminContractTest(TestCase):
    def test_user_model_has_role_field(self):
        self.assertIn("role", User.__table__.columns.keys())
        self.assertEqual(User.__table__.columns["role"].default.arg, "user")

    def test_admin_router_prefix(self):
        self.assertEqual(admin.router.prefix, "/api/admin")

    def test_admin_schemas_accept_frontend_aliases(self):
        news = AdminNewsRequest(
            title="标题",
            description="简介",
            content="内容",
            image="/uploads/news/a.jpg",
            author="管理员",
            categoryId=1,
            views=10,
        )
        category = AdminCategoryRequest(name="科技", sortOrder=7)

        self.assertEqual(news.category_id, 1)
        self.assertEqual(category.sort_order, 7)
