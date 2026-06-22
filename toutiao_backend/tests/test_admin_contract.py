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

    def test_admin_router_has_restful_resource_paths(self):
        paths = {route.path for route in admin.router.routes}

        self.assertIn("/api/admin/news", paths)
        self.assertIn("/api/admin/news/{news_id}", paths)
        self.assertIn("/api/admin/categories", paths)
        self.assertIn("/api/admin/categories/{category_id}", paths)
        self.assertIn("/api/admin/users", paths)

    def test_admin_router_does_not_keep_legacy_action_paths(self):
        paths = {route.path for route in admin.router.routes}

        self.assertNotIn("/api/admin/news/list", paths)
        self.assertNotIn("/api/admin/news/add", paths)
        self.assertNotIn("/api/admin/news/update/{news_id}", paths)
        self.assertNotIn("/api/admin/news/delete/{news_id}", paths)
        self.assertNotIn("/api/admin/category/list", paths)
        self.assertNotIn("/api/admin/category/add", paths)
        self.assertNotIn("/api/admin/category/update/{category_id}", paths)
        self.assertNotIn("/api/admin/category/delete/{category_id}", paths)
        self.assertNotIn("/api/admin/users/list", paths)

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
