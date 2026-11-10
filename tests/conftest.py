import shutil
from io import StringIO

import pytest
from django.conf import settings
from django.core.management import call_command
from django.test import override_settings


@pytest.fixture(scope="session")
def media_root(pytestconfig):
    # The test database is reused between runs (--reuse-db), so the media files its
    # images point to must be kept too: store them in pytest's cache folder
    return pytestconfig.cache.mkdir("media")


@pytest.fixture(scope="session", autouse=True)
def test_storages(media_root):
    with override_settings(
        MEDIA_ROOT=media_root,
        STORAGES={
            # Never write test media to S3 or to the project's medias/ folder
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            # Plain copies: the manifest storage's post-processing isn't needed in tests
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        },
    ):
        yield


@pytest.fixture(scope="session")
def django_db_setup(test_storages, media_root, django_db_setup, django_db_blocker):
    """Run the deploy steps on the test database, like on Scalingo, unless it's reused and already has them."""
    from sites_conformes.core.models import ContentPage

    out = StringIO()
    with django_db_blocker.unblock():
        if ContentPage.objects.filter(slug="page_templates_index").exists():
            if not any(media_root.iterdir()):
                raise pytest.UsageError(
                    "The reused test database refers to media files that no longer exist "
                    "(was .pytest_cache cleared?): rebuild it with `make test ARGS=--create-db`"
                )
            if not settings.STATIC_ROOT.is_dir():
                call_command("collectstatic", interactive=False, verbosity=0, stdout=out, stderr=out)
            return

        # New test database: start from empty media
        shutil.rmtree(media_root)
        media_root.mkdir()
        # Like the Scalingo build: create_starter_pages imports the DSFR pictograms and
        # illustrations from the collected statics, through paths relative to the current
        # directory ("staticfiles/..."), so tests must run from the project root.
        call_command("collectstatic", interactive=False, verbosity=0, stdout=out, stderr=out)
        # Same commands as the postdeploy step in the Procfile
        call_command("create_starter_pages", stdout=out, stderr=out)
        call_command("import_page_templates", stdout=out, stderr=out)
