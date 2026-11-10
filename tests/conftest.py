from io import StringIO

import pytest
from django.core.management import call_command
from django.test import override_settings


@pytest.fixture(scope="session", autouse=True)
def test_storages(tmp_path_factory):
    with override_settings(
        MEDIA_ROOT=tmp_path_factory.mktemp("media"),
        STORAGES={
            # Never write test media to S3 or to the project's medias/ folder
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            # Plain copies: the manifest storage's post-processing isn't needed in tests
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        },
    ):
        yield


@pytest.fixture(scope="session")
def django_db_setup(test_storages, django_db_setup, django_db_blocker):
    """Create the test database once, then run the deploy steps on it, like on Scalingo."""
    out = StringIO()
    with django_db_blocker.unblock():
        # Like the Scalingo build: create_starter_pages imports the DSFR pictograms and
        # illustrations from the collected statics, through paths relative to the current
        # directory ("staticfiles/..."), so tests must run from the project root.
        call_command("collectstatic", interactive=False, verbosity=0, stdout=out, stderr=out)
        # Same commands as the postdeploy step in the Procfile
        call_command("create_starter_pages", stdout=out, stderr=out)
        call_command("import_page_templates", stdout=out, stderr=out)
