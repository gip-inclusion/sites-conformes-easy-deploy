"""
Minimal settings for a Sites Conformes instance.

Based on https://numerique-gouv.github.io/sites-conformes/paquet/installation.html
and on upstream's config/settings.py. Everything is configured through
environment variables (see .env.example).
"""

import os
from pathlib import Path

import dj_database_url
import sites_conformes
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

load_dotenv()

PROJECT_DIR = Path(__file__).resolve().parent.parent
PACKAGE_DIR = Path(sites_conformes.__file__).resolve().parent

# The sites_conformes package locates some of its bundled data files with
# settings.BASE_DIR / "sites_conformes/...", as if running from an upstream
# checkout (e.g. import_page_templates, create_demo_pages). Point BASE_DIR at the
# directory containing the installed package so those paths resolve, and use
# PROJECT_DIR for this project's own files.
BASE_DIR = PACKAGE_DIR.parent


def getenv_bool(key: str, default: bool) -> bool:
    try:
        value = os.environ[key]
    except KeyError:
        return default
    return value.casefold() in ("1", "true")


SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = getenv_bool("DEBUG", False)
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,.localhost").split(",")

HOST_PROTO = os.getenv("HOST_PROTO", "https")
HOST_URL = os.getenv("HOST_URL", "localhost")
HOST_PORT = os.getenv("HOST_PORT", "")
FORCE_SCRIPT_NAME = os.getenv("FORCE_SCRIPT_NAME", "").rstrip("/")

# TLS is terminated by the hosting proxy (e.g. Scalingo): trust the public origins
# so that Django's CSRF origin check accepts HTTPS form posts (admin login, etc.).
CSRF_TRUSTED_ORIGINS = [
    f"{HOST_PROTO}://{host}" + (f":{HOST_PORT}" if HOST_PORT else "")
    for host in ALLOWED_HOSTS
    if host not in ("127.0.0.1", "localhost", ".localhost")
]
CSRF_TRUSTED_ORIGINS += list(filter(None, os.getenv("CSRF_TRUSTED_ORIGINS", "").replace(" ", "").split(",")))

# Settings read by the sites_conformes package
SF_USE_DB_STORAGE = False
SF_NOINDEX = getenv_bool("SF_NOINDEX", False)
SF_PUBLIC_CACHE_MAX_AGE = int(os.getenv("SF_PUBLIC_CACHE_MAX_AGE", 0))
SF_DISABLE_TUTORIALS = getenv_bool("SF_DISABLE_TUTORIALS", False)
PROCONNECT_ACTIVATED = False
TESTING = False

# Two-factor authentication: optional by default, every admin user must set it up when required
WAGTAIL_2FA_REQUIRED = getenv_bool("WAGTAIL_2FA_REQUIRED", False)
WAGTAIL_2FA_OTP_TOTP_NAME = os.getenv("WAGTAIL_2FA_OTP_TOTP_NAME", os.getenv("SITE_NAME", "Sites Conformes"))

# Applications

INSTALLED_APPS = [
    "storages",
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.settings",
    "wagtail.contrib.typed_table_block",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.snippets",
    "wagtail",
    "wagtailmarkdown",
    "wagtailmenus",  # Obsolete upstream, but still needed for its models/migrations
    "wagtail_localize",
    "wagtail_localize.locales",
    "modelcluster",
    "taggit",
    "wagtail.api.v2",
    "rest_framework",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.humanize",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "dsfr",
    "sites_conformes",
    "sites_conformes.customimages",
    "sites_conformes.core",
    "sites_conformes.blog",
    "sites_conformes.events",
    "sites_conformes.forms",
    "sites_conformes.menus",
    "wagtail_honeypot",
    "sites_conformes.dashboard",
    "wagtail.admin",
    # Two-factor authentication for the admin, used by
    # sites_conformes.dashboard.middleware.VerifyUserStaticFilesMiddleware
    "wagtail_2fa",
    "django_otp",
    "django_otp.plugins.otp_totp",
]

MIDDLEWARE = [
    "sites_conformes.core.middleware.NoIndexMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "sites_conformes.dashboard.middleware.VerifyUserStaticFilesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "sites_conformes.core.middleware.IframeMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [PACKAGE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "wagtail.contrib.settings.context_processors.settings",
                "wagtailmenus.context_processors.wagtailmenus",
                "sites_conformes.core.context_processors.skiplinks",
                "sites_conformes.core.context_processors.mega_menus",
                "sites_conformes.core.context_processors.iframe",
            ],
        },
    },
]

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    raise ValueError("Please set the DATABASE_URL environment variable")

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 15}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization

LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True
WAGTAIL_I18N_ENABLED = True
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", "English"),
    ("fr", "Français"),
]
LOCALE_PATHS = [PACKAGE_DIR / "locale"]

# Static and media files

STATIC_URL = "static/"
STATIC_ROOT = PROJECT_DIR / "staticfiles"
STATICFILES_DIRS = [PACKAGE_DIR / "static"]

# Service deployed by this instance. Its favicons/<SERVICE_NAME>/ folder, if any, is
# served in place of the DSFR favicon files with the same name; missing files fall
# back to the DSFR ones. Static files are collected at build time, so changing it
# requires a redeploy.
SERVICE_NAME_CHOICES = ["data-inclusion", "mon-recap", "site-institutionnel"]
SERVICE_NAME = os.getenv("SERVICE_NAME", "")
if SERVICE_NAME and SERVICE_NAME not in SERVICE_NAME_CHOICES:
    raise ImproperlyConfigured(
        f"Unknown SERVICE_NAME {SERVICE_NAME!r}, expected one of: {', '.join(SERVICE_NAME_CHOICES)}"
    )

FAVICONS_DIR = PROJECT_DIR / "statics" / "favicons"
if SERVICE_NAME and (FAVICONS_DIR / SERVICE_NAME).is_dir():
    STATICFILES_DIRS.insert(0, ("dsfr/dist/favicon", FAVICONS_DIR / SERVICE_NAME))
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}

# django-dsfr adds integrity (SRI) hashes of its original CSS/JS files to the page, but the
# manifest storage rewrites the url() references inside the CSS when collecting statics, so
# the served files no longer match and browsers refuse them: the DSFR layout breaks on
# public pages. django-dsfr enables the checksums unless this is explicitly False.
DSFR_USE_INTEGRITY_CHECKSUMS = False

# Media files go to S3 when S3_HOST is set, otherwise to the local filesystem.
# See https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html
if os.getenv("S3_HOST"):
    s3_protocol = os.getenv("S3_PROTOCOL", "https")
    s3_endpoint_url = f"{s3_protocol}://{os.environ['S3_HOST']}"
    s3_bucket_name = os.environ["S3_BUCKET_NAME"]
    s3_public_host = os.getenv("S3_PUBLIC_HOST", "")

    s3_options = {
        "bucket_name": s3_bucket_name,
        "access_key": os.environ["S3_KEY_ID"],
        "secret_key": os.environ["S3_KEY_SECRET"],
        "endpoint_url": s3_endpoint_url,
        "region_name": os.getenv("S3_BUCKET_REGION", "fr"),
        "file_overwrite": False,
        "location": os.getenv("S3_LOCATION", ""),
    }

    if s3_public_host:
        # Presigned URLs are bound to the endpoint hostname, so signing is disabled
        # when the public host differs from the internal endpoint (e.g. MinIO).
        s3_options["custom_domain"] = f"{s3_public_host}/{s3_bucket_name}"
        s3_options["url_protocol"] = f"{s3_protocol}:"
        s3_options["querystring_auth"] = False
        s3_public_endpoint = f"{s3_protocol}://{s3_public_host}"
    else:
        s3_public_endpoint = s3_endpoint_url

    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": s3_options}
    MEDIA_URL = f"{s3_public_endpoint}/"
else:
    STORAGES["default"] = {"BACKEND": "django.core.files.storage.FileSystemStorage"}
    MEDIA_URL = os.getenv("MEDIA_URL", "medias/")
    MEDIA_ROOT = PROJECT_DIR / os.getenv("MEDIA_ROOT", "medias")

if DEBUG:
    STORAGES["staticfiles"] = {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}

# Wagtail

WAGTAIL_SITE_NAME = os.getenv("SITE_NAME", "Sites Conformes")
WAGTAILADMIN_PATH = os.getenv("WAGTAILADMIN_PATH", "cms-admin/")
WAGTAILADMIN_BASE_URL = f"{HOST_PROTO}://{HOST_URL}" + (f":{HOST_PORT}" if HOST_PORT else "")
WAGTAILAPI_BASE_URL = WAGTAILADMIN_BASE_URL
LOGIN_URL = f"{FORCE_SCRIPT_NAME}/{WAGTAILADMIN_PATH}login/"
LOGOUT_URL = f"{FORCE_SCRIPT_NAME}/{WAGTAILADMIN_PATH}logout/"
WAGTAIL_FRONTEND_LOGIN_URL = LOGIN_URL
WAGTAIL_PASSWORD_REQUIRED_TEMPLATE = "sites_conformes_core/password_required.html"  # nosec B105
WAGTAIL_GRAVATAR_PROVIDER_URL = None
WAGTAIL_ENABLE_UPDATE_CHECK = False
WAGTAILIMAGES_IMAGE_MODEL = "sites_conformes_customimages.CustomImage"
WAGTAILIMAGES_EXTENSIONS = ["gif", "jpg", "jpeg", "png", "webp", "svg"]
WAGTAILDOCS_EXTENSIONS = ["pdf", "docx", "odt", "xlsx", "ods", "pptx", "odp", "csv", "txt"]
WAGTAILEMBEDS_RESPONSIVE_HTML = True
WAGTAIL_MODERATION_ENABLED = False
WAGTAILADMIN_USER_PASSWORD_RESET_FORM = "sites_conformes.dashboard.forms.DsfrPasswordResetForm"  # nosec B105
# "Forgot password" needs working email settings, which this project doesn't configure yet
WAGTAIL_PASSWORD_RESET_ENABLED = getenv_bool("WAGTAIL_PASSWORD_RESET_ENABLED", False)
HONEYPOT_ENABLED_DEFAULT = True
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10_000

# Admin dashboard notifications and new-version check
NOTIFICATIONS_FILE_URL = (
    "https://raw.githubusercontent.com/numerique-gouv/sites-conformes/refs/heads/main/notifications.json"
)
LATEST_RELEASE_URL = "https://api.github.com/repos/numerique-gouv/sites-conformes/releases/latest"
RELEASES_URL = "https://github.com/numerique-gouv/sites-conformes/releases"
ADVERTISE_LATEST_VERSION = True

# Logging: send everything to stderr so that errors (including 500 tracebacks,
# which Django only emails to ADMINS by default when DEBUG is off) show up in
# the platform logs.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": os.getenv("LOG_LEVEL", "INFO"),
    },
}
