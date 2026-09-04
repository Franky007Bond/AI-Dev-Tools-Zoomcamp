import pytest
from django.test import Client

from tests.paths import STATIC_DIR


@pytest.mark.django_db
def test_tablet_css_readme_exists():
    css_readme = STATIC_DIR / "CSS.md"
    assert css_readme.exists()
    text = css_readme.read_text(encoding="utf-8")
    assert "1280" in text
    assert "1920" in text


@pytest.mark.django_db
def test_pages_include_tablet_stylesheet(client):
    for url in ("/", "/chore-pool/", "/review-pending/"):
        response = client.get(url)
        assert "tablet.css" in response.content.decode()
