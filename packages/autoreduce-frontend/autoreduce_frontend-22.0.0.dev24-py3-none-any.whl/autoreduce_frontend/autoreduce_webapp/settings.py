# ############################################################################### #
# Autoreduction Repository : https://github.com/autoreduction/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
import os

from autoreduce_db.autoreduce_django.settings import DATABASES as autoreduce_db_settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with these turned on in production!

# Enable debug by default, this allows us to serve static content without
# having to run `manage.py collectstatic` each time. On production
# we use Apache to serve static content instead.
DEBUG = False
if not "AUTOREDUCTION_PRODUCTION" in os.environ:
    DEBUG = True

DEBUG_PROPAGATE_EXCEPTIONS = True
DEBUG_TOOLBAR_AVAILABLE = False
if DEBUG:
    import importlib
    debug_toolbar_spec = importlib.util.find_spec("debug_toolbar")
    found = debug_toolbar_spec is not None
    if found:
        DEBUG_TOOLBAR_AVAILABLE = True

debug_hosts = "127.0.0.1 localhost reducedev2.isis.cclrc.ac.uk"
prod_hosts = "127.0.0.1 localhost 0.0.0.0 reduce.isis.cclrc.ac.uk"

if DEBUG:
    ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', debug_hosts).split()
else:
    ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', prod_hosts).split()

INTERNAL_IPS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'autoreduce_frontend.autoreduce_webapp',
    'autoreduce_frontend.generate_token',
    'autoreduce_db.reduction_viewer',
    'autoreduce_db.instrument',
    'rest_framework.authtoken',
    'django_filters',
    'crispy_forms',
    'django_tables2',
    'hurricane',
]

if DEBUG and DEBUG_TOOLBAR_AVAILABLE:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'
DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"

if DEBUG and DEBUG_TOOLBAR_AVAILABLE:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')

AUTHENTICATION_BACKENDS = [
    'autoreduce_frontend.autoreduce_webapp.backends.UOWSAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'autoreduce_frontend.autoreduce_webapp.context_processors.support_email_processor',
            ],
        },
    },
]

ROOT_URLCONF = 'autoreduce_frontend.autoreduce_webapp.urls'

WSGI_APPLICATION = 'autoreduce_frontend.autoreduce_webapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = autoreduce_db_settings

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
if not DEBUG:
    STATIC_ROOT = '/var/www/api'
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# ICAT
ICAT = {
    'AUTH': os.getenv('ICAT_AUTH'),
    'URL': os.getenv('ICAT_HOST'),
    'USER': os.getenv('ICAT_USER'),
    'PASSWORD': os.getenv('ICAT_PASSWORD')
}

# Outdated Browsers

OUTDATED_BROWSERS = {
    'IE': 9,
}

# UserOffice WebService

UOWS_URL = 'https://api.facilities.rl.ac.uk/ws/UserOfficeWebService?wsdl'
UOWS_LOGIN_URL = 'https://users.facilities.rl.ac.uk/auth/?service=https://reduce.isis.cclrc.ac.uk&redirecturl='

# Email for notifications

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'exchsmtp.stfc.ac.uk'
EMAIL_PORT = 25
EMAIL_ERROR_RECIPIENTS = ['isisreduce@stfc.ac.uk']
EMAIL_ERROR_SENDER = 'autoreducedev@reduce.isis.cclrc.ac.uk'
BASE_URL = 'https://reduce.isis.cclrc.ac.uk/'

# Constant vars
SESSION_COOKIE_AGE = 3600  # The MAX length before user is logged out, 1 hour in seconds
FACILITY = "ISIS"
PRELOAD_RUNS_UNDER = 100  # If the index run list has fewer than this many runs to show the user, preload them all.
CACHE_LIFETIME = 3600  # Objects in ICATCache live this many seconds when ICAT is available to update them.
USER_ACCESS_CHECKS = False  # Should the webapp prevent users from accessing runs/instruments they're not allowed to?

# If the installation is in a development environment, set this variable to True so that
# we are not constrained by having to log in through the user office. This will authenticate
# anyone visiting the site as a super user. It defaults to the DEBUG value
DEVELOPMENT_MODE = DEBUG
X_FRAME_OPTIONS = 'SAMEORIGIN'  # Enables the use of frames within HTML
CONN_MAX_AGE = 60

# If this request header is present then set https.
# Currently this is attached to the request when it goes through the proxy server
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
DATA_ANALYSIS_BASE_URL = "https://data.analysis.stfc.ac.uk/data/browse/#INSTRUMENT/"  # note: the trailing / is important

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
