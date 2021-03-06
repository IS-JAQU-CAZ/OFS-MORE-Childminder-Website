from .base import *

# You should never enable this in production, even if it's temporarily
# All INSTALLED_APPS in django relies on this variable, like google-analytics app.
DEBUG = False

ALLOWED_HOSTS = ['*']

PROD_APPS = [
    'whitenoise',
]

INSTALLED_APPS = BUILTIN_APPS + THIRD_PARTY_APPS + PROD_APPS + PROJECT_APPS

URL_PREFIX = '/childminder'
STATIC_URL = URL_PREFIX + '/static/'

AUTHENTICATION_URL = URL_PREFIX + '/sign-in/'

AUTHENTICATION_EXEMPT_URLS = (
    r'^' + URL_PREFIX + '/$',
    r'^' + URL_PREFIX + '/account/account/$',
    r'^' + URL_PREFIX + '/account/email/$',
    r'^' + URL_PREFIX + '/security-question/$',
    r'^' + URL_PREFIX + '/email-sent/$',
    r'^' + URL_PREFIX + '/validate/.*$',
    r'^' + URL_PREFIX + '/code-resent/.*$',
    r'^' + URL_PREFIX + '/security-code/.*$',
    r'^' + URL_PREFIX + '/link-used/$',
    r'^' + URL_PREFIX + '/link-expired/$',
    r'^' + URL_PREFIX + '/new-code/.*$',
    r'^' + URL_PREFIX + '/djga/+',
    r'^' + URL_PREFIX + '/sign-in/',
    r'^' + URL_PREFIX + '/sign-in/check-email/',
    r'^' + URL_PREFIX + '/email-resent/',
    r'^' + URL_PREFIX + '/sign-in/new-application/',
    r'^' + URL_PREFIX + '/new-application/',
    r'^' + URL_PREFIX + '/new-application/check-email/',
    r'^' + URL_PREFIX + '/service-unavailable/',
    r'^' + URL_PREFIX + '/help-contact/',
    r'^' + URL_PREFIX + '/application-saved/$',
    r'^' + URL_PREFIX + '/health-check/(?P<id>[\w-]+)/$',
    r'^' + URL_PREFIX + '/feedback/',
    r'^' + URL_PREFIX + '/feedback-submitted/',
    r'^' + URL_PREFIX + '/documents-needed/',
    r'^' + URL_PREFIX + '/home-ready/',
    r'^' + URL_PREFIX + '/prepare-interview/'
)

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('POSTGRES_DB', 'postgres'),
        'USER': os.environ.get('POSTGRES_USER', 'ofsted'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'OfstedB3ta'),
        'HOST': os.environ.get('POSTGRES_HOST', 'ofsted-postgres'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432')
    }
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# Automatic Django logging at the INFO level (i.e everything the comes to the console when ran locally)
LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'formatters': {
    'console': {
            # exact format is not important, this is the minimum information
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        },
  'handlers': {
    'django.server': {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'maxBytes': 1 * 1024 * 1024,
        'filename': 'logs/output.log',
        'formatter': 'console',
        'maxBytes': 1 * 1024 * 1024,
        'backupCount': 30
    },
   },
   'loggers': {
     'django.server': {
       'handlers': ['django.server'],
         'level': 'INFO',
           'propagate': True,
      },
    },
}