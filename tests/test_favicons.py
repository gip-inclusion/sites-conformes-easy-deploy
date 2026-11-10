from pathlib import Path

import dsfr
import pytest
from django.conf import settings

DSFR_FAVICON_DIR = Path(dsfr.__file__).resolve().parent / "static/dsfr/dist/favicon"


def test_favicon_folders_match_service_names():
    # A folder named after an unknown service would never be used
    folders = {d.name for d in settings.FAVICONS_DIR.iterdir() if d.is_dir()}
    assert folders <= set(settings.SERVICE_NAME_CHOICES)


@pytest.mark.parametrize("service", settings.SERVICE_NAME_CHOICES)
def test_favicon_folder_only_contains_dsfr_file_names(service):
    # A file that doesn't match a DSFR favicon file name would never be used
    folder = settings.FAVICONS_DIR / service
    if not folder.is_dir():
        pytest.skip(f"no favicons for {service}")
    files = {f.name for f in folder.iterdir() if not f.name.startswith(".")}
    assert files <= {f.name for f in DSFR_FAVICON_DIR.iterdir()}
