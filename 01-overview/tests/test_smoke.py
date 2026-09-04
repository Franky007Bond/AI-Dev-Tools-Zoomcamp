from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ProjectSmokeTests(SimpleTestCase):
    def test_django_settings_are_configured(self):
        self.assertTrue(settings.configured)
        self.assertEqual(settings.ROOT_URLCONF, "homework_quest.urls")

    def test_admin_login_page_loads(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_database_is_not_developer_sqlite(self):
        name = Path(str(settings.DATABASES["default"]["NAME"]))
        self.assertNotEqual(name, settings.BASE_DIR / "db.sqlite3")
