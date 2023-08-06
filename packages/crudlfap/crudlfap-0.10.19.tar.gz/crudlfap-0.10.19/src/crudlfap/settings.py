"""
A settings file to import boilerplate from.

.. py:data:: AUTHENTICATION_BACKENDS

    Contains the default django.contrib.auth.backends.ModelBackend and
    also crudlfap_auth.backends.ViewBackend which will introspect the
    view's authenticate and allowed_groups variables.

.. py:data:: CRUDLFAP_VIEWS

    List of default views to provide to Routers that were not spawned with any
    view.

.. py:data:: INSTALLED_APPS

    That list contains both :py:data:`CRUDLFAP_APPS` and :py:data:`DJANGO_APPS`
    and you can use them as such on a new project:

    .. code-block:: python

        from crudlfap.settings import INSTALLED_APPS

        INSTALLED_APPS = ['yourapp'] + INSTALLED_APPS

.. py:data:: CRUDLFAP_APPS

    List of apps CRUDLFA+ depends on, you can use it as such:

    .. code-block:: python

        from crudlfap.settings import CRUDLFAP_APPS

        INSTALLED_APPS = [
            'yourapp',
            'django.contrib.staticfiles',
            # etc
        ] + CRUDLFAP_APPS

.. py:data:: DJANGO_APPS

    This list contains all contrib apps from the Django project that CRUDLFA+
    should depend on. You can use it as such:

    .. code-block:: python

        from crudlfap.settings import CRUDLFAP_APPS, DJANGO_APPS

        INSTALLED_APPS = ['yourapp'] + CRUDLFAP_APPS + DJANGO_APPS

.. py:data:: TEMPLATES

    This list contains both :py:data:`DEFAULT_TEMPLATE_BACKEND` and
    :py:data:`CRUDLFAP_TEMPLATE_BACKEND` and works out of the box on an empty
    project. You can add it to your settings file by just importing it:

    .. code-block:: python

        from crudlfap.settings import TEMPLATES

.. py:data:: CRUDLFAP_TEMPLATE_BACKEND

   Configuration for Jinja2 and environment expected by
   CRUDLFA+ default templates. Add it to your own TEMPLATES setting using
   import:

    .. code-block:: python

       from crudlfap.settings import CRUDLFAP_TEMPLATE_BACKEND

       TEMPLATES = [
           # YOUR_BACKEND
           CRUDLFAP_TEMPLATE_BACKEND,
       ]

.. py:data:: DEFAULT_TEMPLATE_BACKEND

    Configuration for Django template backend with all builtin context
    processors. You can use it to define only your third backend as such:

    .. code-block:: python

        from crudlfap.settings import (
            CRUDLFAP_TEMPLATE_BACKEND,
            DEFAULT_TEMPLATE_BACKEND,
        )

        TEMPLATES = [
           # YOUR_BACKEND
           CRUDLFAP_TEMPLATE_BACKEND,
           DEFAULT_TEMPLATE_BACKEND,
        ]

.. py:data:: DEBUG

    Evaluate ``DEBUG`` env var as boolean, False by default.

.. py:data:: SECRET_KEY

    Get ``SECRET_KEY`` env var, or be ``'notsecret'`` by default.

    .. danger:: Raises an Exception if it finds both SECRET_KEY=notsecret and
                DEBUG=False.

.. py:data:: ALLOWED_HOSTS

    Split ``ALLOWED_HOSTS`` env var with commas, or be ``['*']`` by default.

    .. danger:: Raises an Exception if it finds both ALLOWED_HOSTS to be
                ``'*'`` and DEBUG=False.

.. py:data:: MIDDLEWARE

    A default MIDDLEWARE configuration you can import.

.. py:data:: OPTIONAL_APPS

    from crudlfap.settings import *
    # [...] your settings
    install_optional(OPTIONAL_APPS, INSTALLED_APPS)
    install_optional(OPTIONAL_MIDDLEWARE, MIDDLEWARE)

"""


import os
import sys
from pathlib import Path

from crudlfap.conf import install_optional  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'notsecret')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(os.environ.get('DEBUG', False))

if 'HOST' in os.environ:
    ALLOWED_HOSTS = ['www.' + os.environ.get('HOST'), os.environ.get('HOST')]
elif DEBUG and 'ALLOWED_HOSTS' not in os.environ:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

CRUDLFAP_VIEWS = [
    'crudlfap.views.generic.CreateView',
    'crudlfap.views.generic.DeleteView',
    'crudlfap.views.generic.UpdateView',
    'crudlfap.views.generic.DetailView',
    'crudlfap.views.generic.ListView',
]

CRUDLFAP_APPS = [
    'crudlfap',
    'crudlfap_sites',
    'django_filters',
    'django_tables2',
    'crudlfap_auth',
    'ryzom',
    'py2js',
    'ryzom_django',
    'ryzom_django_mdc',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',
]

INSTALLED_APPS = DJANGO_APPS + CRUDLFAP_APPS

# CRUDLFA+ optional dependencies
OPTIONAL_APPS = [
    {'debug_toolbar': {'after': 'django.contrib.staticfiles'}},
    {'django_extensions': {'before': 'crudlfap'}},
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'ryzom_unpoly.middleware.UnpolyMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

OPTIONAL_MIDDLEWARE = [
    {'debug_toolbar.middleware.DebugToolbarMiddleware': None}
]

INTERNAL_IPS = ('127.0.0.1',)

CRUDLFAP_TEMPLATE_BACKEND = {
    'BACKEND': 'ryzom_django.template_backend.Ryzom',
    'NAME': 'ryzom',
}

DEFAULT_TEMPLATE_BACKEND = {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}

TEMPLATES = [CRUDLFAP_TEMPLATE_BACKEND, DEFAULT_TEMPLATE_BACKEND]
LOGIN_REDIRECT_URL = '/'
LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

WSGI_APPLICATION = 'crudlfap_example.wsgi.application'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'crudlfap_auth.backends.ViewBackend',
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DB_NAME', 'db.sqlite3'),
        'HOST': os.getenv('DB_HOST'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASS'),
    }
}

EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', None)
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', None)
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@electeez.com')

if EMAIL_HOST:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


REGISTRATION_OPEN = True     # django-registration
ACCOUNT_ACTIVATION_DAYS = 7  # django-registration
LOGIN_REDIRECT_URL = '/'     # django.contrib.auth
USE_X_FORWARDED_HOST = True  # reverse proxy support

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',  # noqa
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = os.getenv('STATIC_URL', '/static/')
STATIC_ROOT = os.getenv(
    'STATIC_ROOT',
    Path(os.path.dirname(__file__)) / 'public'
)
if 'collectstatic' in sys.argv or not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'  # noqa

UWSGI_SPOOLER_MOUNT = os.getenv('UWSGI_SPOOLER_MOUNT')
UWSGI_SPOOLER_NAMES = os.getenv('UWSGI_SPOOLER_NAMES', '').split(',')
if UWSGI_SPOOLER_MOUNT and UWSGI_SPOOLER_NAMES:
    for name in UWSGI_SPOOLER_NAMES:
        path = os.path.join(UWSGI_SPOOLER_MOUNT, name)
        if not os.path.exists(path):
            os.makedirs(path)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
