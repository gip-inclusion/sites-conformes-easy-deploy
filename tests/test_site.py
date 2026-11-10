"""
Smoke tests: the project boots, the deploy commands run, and the main pages render.

Most of them are regression tests for integration issues between this project and
the sites_conformes package (missing apps, URLs or data files).
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.urls import reverse
from sites_conformes.core.models import ContentPage

pytestmark = pytest.mark.django_db


def test_system_checks():
    call_command("check", stdout=StringIO())


def test_page_templates_are_imported():
    # Regression: the package looks for its data file under settings.BASE_DIR
    assert ContentPage.objects.filter(slug="page_templates_index").exists()


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    # the DSFR integrity hashes don't match the statics rewritten by the
    # manifest storage, so browsers would refuse the DSFR CSS and JS
    assert b"integrity=" not in response.content


def test_home_page_as_editor(admin_client):
    response = admin_client.get("/")
    assert response.status_code == 200


def test_admin_login_page(client):
    response = client.get(reverse("wagtailadmin_login"))
    assert response.status_code == 200


def test_admin_dashboard(admin_client):
    response = admin_client.get(reverse("wagtailadmin_home"))
    assert response.status_code == 200


def test_javascript_catalog(client):
    response = client.get(reverse("javascript-catalog"))
    assert response.status_code == 200


def test_pages_api(client):
    response = client.get("/api/v2/pages/")
    assert response.status_code == 200


@pytest.mark.parametrize("path", ["/static/dsfr/dist/dsfr.min.css", "/static/wagtailadmin/css/core.css"])
def test_static_files_are_served(client, path):
    # Regression: without WhiteNoise, gunicorn doesn't serve /static/ and the layout breaks
    response = client.get(path)
    assert response.status_code == 200
    response.close()


def test_sitemap(client):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
