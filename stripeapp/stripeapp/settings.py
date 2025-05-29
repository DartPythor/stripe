from pathlib import Path

import environ
from django.conf.global_settings import STATIC_ROOT
from dotenv import load_dotenv

env = environ.Env()
environ.Env.read_env()
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = (
    env(
        "SECRET_KEY",
        cast=str,
        default="django-insecure-mdvnoln%ud#8ky7@45nv!&-mlu7qs%zwd)--!$@$fza#2g21sy",
    ),
)

DEBUG = env("DEBUG", cast=bool, default=True)

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "payments.apps.PaymentsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stripeapp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "stripeapp.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

STATIC_ROOT = BASE_DIR / "static"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

STRIPE_SECRET_KEY = env(
    "STRIPE_SECRET_KEY",
    cast=str,
    default="sk_test_51RTpqfD5FxV2LJUjdFmuDTtrW5Gw9Wd06kaZmdLzUsS3GlxQDZj784NmZwaNBkBnxkN67Mub5NBtRY1dsqbtBh7x00deMXDIk6",
)

STRIPE_PUBLISHABLE_KEY = env(
    "STRIPE_PUBLISHABLE_KEY",
    cast=str,
    default="pk_test_51RTpqfD5FxV2LJUj25ZEMMG0Uk3dMdK41KuunxlqWYWwtsjbpZRMEvJozQS2K5r7ynCmZo8aLnpTR4MN6PTYw5hG00HV9Q3AK0",
)
